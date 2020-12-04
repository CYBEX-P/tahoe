from vt_py import vt
from vt_api_key import API_key as APIK


#the number of security engines and systems the system as run through (aka the total).
total_engines = 0

# Create client-side connection to the VT API
tahoe_VTAPI_query = vt.Client(APIK)

# Create a url_id token with the url_objects provided URL
# example URL used from openphish
VT_url_id = vt.url_id('https://pochtarefund-xeq16m.aakny.xyz/tvl/payment/tsb/indexx.html')
url_stats =  tahoe_VTAPI_query.get_object("/urls/{}", VT_url_id) 

# This is the where the actual query is made so the the VT API
# url_stats = tahoe_VTAPI_query.user("/urls/{}",VT_url_id)

malicious_score = url_stats.last_analysis_stats["malicious"]

for key, value in url_stats.last_analysis_stats.items():
    total_engines += int(value)

malicious_and_total_score = str(malicious_score) + "/" + str(total_engines)

print("The malicious score is:" ,malicious_and_total_score)

tahoe_VTAPI_query.close()