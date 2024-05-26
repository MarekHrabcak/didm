import { Component, OnInit } from '@angular/core';

import { AgentService } from 'src/app/services/agent.service';
import { AgentStatus } from 'src/app/enums/agent-status.enum';

import { map } from 'rxjs/operators';
import { KeycloakService } from 'keycloak-angular';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.scss'],
})
export class NavComponent implements OnInit {
  agentStatus = AgentStatus;
  status = this.agentStatus.Loading;
  isLoggedIn: boolean
  userProfile = null
  navColor: string = '#ffffff';

  constructor(private agentService: AgentService, private keycloakService: KeycloakService) { }

  async ngOnInit() {
    this.agentService.getStatus()
      .pipe(
        map((status) => this.status = status)
      )
      .subscribe();

    this.isLoggedIn = await this.keycloakService.isLoggedIn()
    if (this.isLoggedIn) {
      this.userProfile = await this.keycloakService.loadUserProfile()
      this.keycloakService.getToken()
        .then(token => {
          const decodedToken = JSON.parse(atob(token.split('.')[1]));
          const color = decodedToken['nco'];

          this.navColor = color;
        });
    }
  }

  public logout() {
    this.keycloakService.logout()
  }

}
