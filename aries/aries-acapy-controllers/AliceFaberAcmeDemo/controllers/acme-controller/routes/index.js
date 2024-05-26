const express = require('express');
const router = express.Router();

/* GET home page. */
router.get('/', async function(req, res, next) {
  const NavLinkService = require('../services/NavLinkService');
  const navLinkService = new NavLinkService();

  res.render('index', { navLinks: navLinkService.getNavLinks() });
});

router.get('/status', async function(req, res, next) {
  const agentServiceFactory = require('../services/AgentService');
  const token = JSON.parse(req.session['keycloak-token'])['access_token']
  const agentService = agentServiceFactory(token)
  
  const status = await agentService.getStatus();
  res.status(200).json({ status: status ? 'up' : 'down' });
});

module.exports = router;
