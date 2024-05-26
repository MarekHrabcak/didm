using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace BlazorAuthSample.Pages
{
    public class LoginModel : PageModel
    {
        public async Task OnGet(string redirectUri)
        {

            // await HttpContext.ChallengeAsync(OpenIdConnectDefaults.AuthenticationScheme, new AuthenticationProperties {
            //     RedirectUri = "http://localhost:5001/"
            // });
            
            // await HttpContext.ChallengeAsync(OpenIdConnectDefaults.AuthenticationScheme, new AuthenticationProperties
            await HttpContext.ChallengeAsync(OpenIdConnectDefaults.AuthenticationScheme, new AuthenticationProperties
            {
                RedirectUri = redirectUri ?? "/"
            });
        }
    }
}