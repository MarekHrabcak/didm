using System.Threading.Tasks;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.AspNetCore.Mvc.RazorPages;
using FaberController.Services;

namespace BlazorAuthSample.Pages
{
    public class LogoutModel : PageModel
    {
        public async Task OnGet()
        {
            
            FCAgentService.Token = null;
            // sign-out from the default authentication scheme
            await HttpContext.SignOutAsync(OpenIdConnectDefaults.AuthenticationScheme, new AuthenticationProperties
            {
                RedirectUri = "/logout"
            });

            // sign-out from the cookie authentication scheme
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            
        }
    }
}