import { BrowserModule } from '@angular/platform-browser';
import { NgModule, APP_INITIALIZER } from '@angular/core';
import { HTTP_INTERCEPTORS } from '@angular/common/http';

import { KeycloakAngularModule, KeycloakEventType, KeycloakService } from 'keycloak-angular';

import { SharedModule } from './shared/shared.module';

import { AppRoutingModule } from './app-routing.module';

import { AppComponent } from './components/app/app.component';
import { NavComponent } from './components/nav/nav.component';
import { NavCardComponent } from './components/nav-card/nav-card.component';
import { NavCardListComponent } from './components/nav-card-list/nav-card-list.component';

import { InterceptorService } from './services/interceptor.service';

function initializeKeycloak(keycloak: KeycloakService) {
  return () => {
    keycloak.keycloakEvents$.subscribe({
      next(event) {
        if (event.type == KeycloakEventType.OnTokenExpired) {
          keycloak.updateToken(20)
        }
      }
    })

    return keycloak.init({
      config: {
        url: 'http://keycloak:8090',
        realm: 'master',
        clientId: 'agent'
      },
      initOptions: {
        onLoad: 'login-required',
        silentCheckSsoRedirectUri: window.location.origin + '/assets/check-sso.html'
      },
      shouldAddToken(request) {
        return true
      },
      authorizationHeaderName: 'X-KEYCLOAK-JWT',
      bearerPrefix: '',
      enableBearerInterceptor: true
    })
  }

}

@NgModule({
  declarations: [
    AppComponent,
    NavCardListComponent,
    NavComponent,
    NavCardComponent
  ],
  imports: [
    BrowserModule,
    SharedModule,
    AppRoutingModule,
    KeycloakAngularModule
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: InterceptorService, multi: true },
    { provide: APP_INITIALIZER, useFactory: initializeKeycloak, multi: true, deps: [KeycloakService] }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
