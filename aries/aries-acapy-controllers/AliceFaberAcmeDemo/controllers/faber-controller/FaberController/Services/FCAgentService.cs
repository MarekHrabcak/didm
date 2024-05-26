using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using FaberController.Enums;
using Newtonsoft.Json.Linq;
using ZXing.Aztec.Internal;

namespace FaberController.Services
{
    public class FCAgentService
    {
        public FCAgentService(HttpClient Http)
        {
            _http = Http;
        }

        private HttpClient _http { get; }
        public static string Token {get; set;}
        public static string Username {get; set;}

        public void SetToken() {
            if (Token == null) {
                return;
            }
            
            if (_http.DefaultRequestHeaders.Contains("X-KEYCLOAK-JWT")) {
                _http.DefaultRequestHeaders.Remove("X-KEYCLOAK-JWT");
            }

            _http.DefaultRequestHeaders.Add("X-KEYCLOAK-JWT", Token); 
        }

        public async Task<AgentStatus> GetStatus()
        {
            try
            {
                SetToken();
                var response = await _http.GetAsync("/status");
                response.EnsureSuccessStatusCode();
                return AgentStatus.Up;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex);
                return AgentStatus.Down;
            }
        }

        public async Task<JArray> GetConnections()
        {
            try
            {
                SetToken();   
                var response = await _http.GetAsync("/connections");
                response.EnsureSuccessStatusCode();

                var responseString = await response.Content.ReadAsStringAsync();
                var jsonResponse = JObject.Parse(responseString);
                return jsonResponse.Value<JArray>("results");
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex);
                return new JArray();
            }
        }

        public async Task<JObject> RemoveConnection(string connectionId)
        {
            SetToken();
            if (connectionId == null || connectionId == "")
            {
                Console.Error.WriteLine("Must provide a connection ID");
                return new JObject();
            }
            try
            {
                using var content = new StringContent("");
                var response = await _http.PostAsync(string.Format("/connections/{0}/remove", connectionId), content);
                response.EnsureSuccessStatusCode();

                var responseString = await response.Content.ReadAsStringAsync();
                return JObject.Parse(responseString);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex);
                return new JObject();
            }
        }

        public async Task<JObject> CreateInvitation()
        {
            SetToken();
            try
            {
                using var content = new StringContent("");
                var response = await _http.PostAsync("/connections/create-invitation", content);
                response.EnsureSuccessStatusCode();

                var responseString = await response.Content.ReadAsStringAsync();
                return JObject.Parse(responseString);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex);
                return new JObject();
            }
        }

        public async Task<JObject> ReceiveInvitation(string invitation)
        {
            SetToken();
            try
            {

                using var content = new StringContent(invitation);
                var response = await _http.PostAsync("/connections/receive-invitation", content);

                response.EnsureSuccessStatusCode();

                var responseString = await response.Content.ReadAsStringAsync();
                return JObject.Parse(responseString);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex);
                return new JObject();
            }
        }

        public async Task<JArray> GetSchemas()
        {
            SetToken();
            try
            {
                var response = await _http.GetAsync("/schemas/created");
                response.EnsureSuccessStatusCode();

                var responseString = await response.Content.ReadAsStringAsync();
                var jsonResponse = JObject.Parse(responseString);
                return jsonResponse.Value<JArray>("schema_ids");

            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex);
                return new JArray();
            }
        }

        public async Task<JObject> GetSchema(string schemaId)
        {
            SetToken();
            try
            {
                var response = await _http.GetAsync(string.Format("/schemas/{0}", schemaId));
                response.EnsureSuccessStatusCode();

                var responseString = await response.Content.ReadAsStringAsync();
                return JObject.Parse(responseString);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex);
                return new JObject();
            }
        }

        public async Task<JArray> GetCredentialDefinitions()
        {
            SetToken();
            try
            {
                var response = await _http.GetAsync("/credential-definitions/created");
                response.EnsureSuccessStatusCode();

                var responseString = await response.Content.ReadAsStringAsync();
                var jsonResponse = JObject.Parse(responseString);
                return jsonResponse.Value<JArray>("credential_definition_ids");

            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex);
                return new JArray();
            }
        }

        public async Task<JObject> GetCredentialDefinition(string credentialDefinitionId)
        {
            SetToken();
            try
            {
                var response = await _http.GetAsync(string.Format("/credential-definitions/{0}", credentialDefinitionId));
                response.EnsureSuccessStatusCode();

                var responseString = await response.Content.ReadAsStringAsync();
                var jsonResponse = JObject.Parse(responseString);
                return jsonResponse.Value<JObject>("credential_definition");
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex);
                return new JObject();
            }
        }

        public async Task<JObject> SendCredential(string credential)
        {
            SetToken();
            try
            {
                using var content = new StringContent(credential, Encoding.UTF8, "application/json");
                content.Headers.ContentType = new MediaTypeHeaderValue("application/json");
                var response = await _http.PostAsync("/issue-credential/send", content);
                 response.EnsureSuccessStatusCode();
                var result = await response.Content.ReadAsStringAsync();

                var responseString = await response.Content.ReadAsStringAsync();
                return JObject.Parse(responseString);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex);
                return new JObject();
            }
        }
    }
}
