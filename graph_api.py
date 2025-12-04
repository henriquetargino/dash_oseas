import requests
import json
import pandas as pd

class GraphAPI:
    def __init__(self, ad_acc, fb_api):
        self.base_url = "https://graph.facebook.com/v13.0/"
        self.api_fields = ["spend", "cpc", "cpm", "impressions", "objective", "adset_name", 
                "adset_id", "clicks", "campaign_name", "campaign_id", 
                "conversions", "frequency", "conversion_values", "ad_name", "ad_id"]
        self.token = "&access_token=" + fb_api

    def get_insights(self, ad_acc, level="campaign"):
        url = self.base_url + "act_" + str(ad_acc)
        url += "/insights?level=" + level
        url += "&fields=" + ",".join(self.api_fields)

        data = requests.get(url + self.token)
        data = json.loads(data._content.decode("utf-8"))

        if "data" not in data:
            print(f"ERRO EM GET_INSIGHTS ({level}):", data) # Mostra o erro

        for i in data.get("data", []):
            if "conversions" in i:
                i["conversion"] = float(i["conversions"][0]["value"])
        return data

    def get_campaigns_status(self, ad_acc):
        url = self.base_url + "act_" + str(ad_acc)
        url += "/campaigns?fields=name,status,adsets{name, id}"
        data = requests.get(url + self.token)
        data = json.loads(data._content.decode("utf-8"))
        
        # --- VERIFICAÇÃO DE ERRO ADICIONADA ---
        if "data" not in data:
            print("ERRO EM GET_CAMPAIGNS_STATUS:", data)
            return {"data": []}
        # ---------------------------------------
        
        return data

    def get_adset_status(self, ad_acc):
        url = self.base_url + "act_" + str(ad_acc)
        url += "/adsets?fields=name,status,id"
        data = requests.get(url + self.token)
        data = json.loads(data._content.decode("utf-8"))
        
        # --- VERIFICAÇÃO DE ERRO ADICIONADA ---
        if "data" not in data:
            print("ERRO EM GET_ADSET_STATUS:", data)
            return {"data": []}
        # ---------------------------------------

        return data

    def get_data_over_time(self, object_id, date_preset="maximum"):
            url = self.base_url + str(object_id)
            url += "/insights?fields="+ ",".join(self.api_fields)
            url += f"&date_preset={date_preset}&time_increment=1"
            url += "&limit=100" 

            data = requests.get(url + self.token)
            data = json.loads(data._content.decode("utf-8"))
            
            if "data" not in data:
                print("ERRO EM GET_DATA_OVER_TIME:", data)
                return {"data": []}

            all_data = data["data"]
            while "paging" in data and "next" in data["paging"]:
                try:
                    data = requests.get(data["paging"]["next"])
                    data = json.loads(data._content.decode("utf-8"))
                    if "data" in data:
                        all_data.extend(data["data"])
                except:
                    break
            
            data["data"] = all_data

            for i in data["data"]:
                if "conversions" in i:
                    i["conversion"] = float(i["conversions"][0]["value"])
            return data

if __name__ == "__main__":
    # Teste rápido direto no arquivo
    fb_api = open("tokens/fb_token").read()
    ad_acc = "775567657455408" # ID que você disse ser o correto
    
    print(f"Testando com Conta: {ad_acc}")
    self = GraphAPI(ad_acc, fb_api)
    
    # Isso vai imprimir o erro no terminal se falhar
    resultado = self.get_adset_status(ad_acc) 
    print("Resultado do Teste:", resultado)