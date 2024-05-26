using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.HttpsPolicy;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using FaberController.Services;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.IdentityModel.Protocols.OpenIdConnect;
using System.Text;
using System.Text.Json;
using System.IdentityModel.Tokens.Jwt;
using System.Net.Http;
using System.IO;

namespace FaberController
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        // For more information on how to configure your application, visit https://go.microsoft.com/fwlink/?LinkID=398940
        public void ConfigureServices(IServiceCollection services)
        {
            services.Configure<CookiePolicyOptions>(options => {
                options.CheckConsentNeeded = _ => false;
                options.MinimumSameSitePolicy = Microsoft.AspNetCore.Http.SameSiteMode.None;
            });

            FCAgentService.Username = "Not logged in";

            services.AddAuthentication(options => {
                // options.DefaultScheme = CookieAuthenticationDefaults.AuthenticationScheme;
                options.DefaultAuthenticateScheme = CookieAuthenticationDefaults.AuthenticationScheme;
                options.DefaultSignInScheme = CookieAuthenticationDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = OpenIdConnectDefaults.AuthenticationScheme;
                // options.DefaultScheme = CookieAu
            }).AddCookie(options => {
                options.LogoutPath = "/logout";
                // options.LoginPath = "/login";
            }).AddOpenIdConnect(async options => {
                options.ClientId = "agent";
                options.Authority = "http://keycloak:8090/realms/master";
                options.RequireHttpsMetadata = false;
                options.SaveTokens = true;
                options.ResponseType = OpenIdConnectResponseType.Code;
                options.GetClaimsFromUserInfoEndpoint = true;

                options.UseSecurityTokenValidator = false;
                
                options.Scope.Clear();
                options.Scope.Add("openid");

                options.Events = new OpenIdConnectEvents
                {
                    OnTokenResponseReceived = context => 
                    {
                        FCAgentService.Token = context.TokenEndpointResponse.AccessToken;
                        var stream = context.TokenEndpointResponse.AccessToken;

                        var handler = new JwtSecurityTokenHandler();
                        var jsonToken = handler.ReadToken(stream) as JwtSecurityToken;
                        
                        FCAgentService.Username = jsonToken.Claims.First(claim => claim.Type == "preferred_username").Value;
                        FCColors.NavColor = jsonToken.Claims.First(claim => claim.Type == "nco").Value;

                        return Task.CompletedTask;
                    },
                };
            });

            services.AddHttpClient<FCAgentService>(c =>
            {
                var agentUrl = Environment.GetEnvironmentVariable("FABER_AGENT_HOST");
                var port = 8080;

                if (agentUrl == null || agentUrl == "") {
                    agentUrl = "localhost";
                }

                var formattedAgentUrl = String.Format("http://{0}:{1}", agentUrl, port);

                Console.WriteLine("Agent is running on: " + formattedAgentUrl);

                c.BaseAddress = new Uri(formattedAgentUrl);
                c.DefaultRequestHeaders.Add("Accept", "application/json");
                c.DefaultRequestHeaders.Add("User-Agent", "FaberController");
            });
            services.AddTransient<FCNavLinkService>();
            services.AddRazorPages();
            services.AddServerSideBlazor();
            // services.AddKeycloakAuthentication(Configuration);
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }
            else
            {
                app.UseExceptionHandler("/Error");
                // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
                app.UseHsts();
            }

            app.UseHttpsRedirection();
            app.UseStaticFiles();

            app.UseRouting();

            app.UseCookiePolicy();
            app.UseAuthentication();
            app.UseAuthorization();


            app.UseEndpoints(endpoints =>
            {
                endpoints.MapBlazorHub();
                endpoints.MapFallbackToPage("/_Host");
            });
        }
    }
}
