from anticaptchaofficial.hcaptchaproxyless import *

def solve_captcha_service(apikey, sitekey):
    solver = hCaptchaProxyless()
    solver.set_key(apikey)
    solver.set_website_url("https://dashboard.render.com")
    solver.set_website_key(sitekey)
    solver.set_is_invisible(1)
    g_response = solver.solve_and_return_solution()
    return g_response
