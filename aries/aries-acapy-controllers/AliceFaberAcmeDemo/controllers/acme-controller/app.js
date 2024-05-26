var createError = require('http-errors');
const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const { engine } = require('express-handlebars');
const helpers = require('handlebars-helpers');

const indexRouter = require('./routes/index');
const connectionRouter = require('./routes/connection');
const proofRouter = require('./routes/proof');

const Keycloak = require('keycloak-connect');
const session = require('express-session');

const app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');
app.engine('hbs', engine({
  extname: 'hbs',
  defaultView: 'default',
  layoutsDir: path.join(__dirname, '/views/layouts/'),
  partialsDir: [
    path.join(__dirname, '/views/partials'),
    path.join(__dirname, '/views/partials/connection'),
    path.join(__dirname, '/views/partials/home'),
    path.join(__dirname, '/views/partials/proof'),
  ],
  helpers: helpers(['array', 'comparison'])
}));

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

var memoryStore = new session.MemoryStore();
var keycloak = new Keycloak({
  store: memoryStore,
  scope: 'openid'
}, {
  realm: 'master',
  'auth-server-url': 'http://keycloak:8090',
  resource: 'agent',
  'public-client': true,
  'confidential-port': 0
})

app.use(session({
  secret: 'averysecretsecret',
  resave: true,
  saveUninitialized: false,
  store: memoryStore
}))

app.use(keycloak.middleware({admin: '/admin'}))

// app.use('/', keycloak.protect())
app.use('/', keycloak.protect(), indexRouter);

// app.use('/connections', keycloak.protect())
app.use('/connections', connectionRouter);

// app.use('/proofs', keycloak.protect())
app.use('/proofs', proofRouter);



// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});



// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
