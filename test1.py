import re
from urllib.parse import unquote

url = "https://click.pstmrk.it/3ts/dashboard.render.com%2Femail-confirm%2F%3Ftoken%3DZfB5G3Vzci1jbm5pZjZpMWhibHM3MzlsOXQwZwU_NGNSRNoJAHmgj78q706w9RHiKea77SL1SAUVznpK/5VpE/dOizAQ/AQ/01cbb01c-ea2a-44b3-9d47-51225bdcbe4c/1/58BL_26AFk"

email_token = re.search(r"token=([^/&]+)", unquote(url))
print(email_token.group(1) if email_token else "Token not found.")
