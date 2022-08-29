import ccxt
import pandas as pd
import requests
import time
from datetime import datetime

#Code créé par Moutonneux : https://github.com/titouannwtt/bot-sniping-kucoin/
#Pensez à utiliser mon lien d'affiliation lors de votre inscription sur Kucoin : 
#https://www.kucoin.com/ucenter/signup?rcode=rPMCW4T    <-----   ou directement code parainage : rPMCW4T

#Cette fonction permet d'obtenir le prix actuel d'une crypto sur Kucoin
def getCurrentPrice(perpSymbol) :
    global kucoin
    try:
        ticker = kucoin.fetchTicker(perpSymbol)
    except BaseException as err:
        print("An error occured", err)
    return float(ticker["ask"])

#Cette fonction permet de créer un ordre
def place_market_order(symbol, side, amount):
    global kucoin
    try:
        return kucoin.createOrder(
            symbol, 
            'market', 
            side, 
            kucoin.amount_to_precision(symbol, amount),
            None
        )
    except Exception as err:
        raise err

#Cette fonction récupère le montant d'USDT de votre compte
def getSolde():
    global kucoin
    try:
        for coin in kucoin.fetchBalance()['info']['data'] :
            if coin['currency']=='USDT' :
                return float(coin['balance'])
    except Exception as err:
        raise err
        
#Connexion à l'API
kucoin = ccxt.kucoin({
            "apiKey": "6305aafbd8c61b00019af3cf",
            "secret": "f4c60b4e-e822-429f-8ca9-1d8e79794e4b",
            "password": "4447190"
            })

#Dans le cas où vos clés API seraient mauvaises, cette fonction renverrait une erreur
try :
    test=getSolde() ; del test
except Exception as err:
    print(f"Problème de connexion à l'API : {err}")
    exit()
print(f"{str(datetime.now()).split('.')[0]} | Connexion à l'API Kucoin réussie.")

kucoin.load_markets()

#place_market_order("SOL-USDT", "buy", getSolde()/getCurrentPrice("SOL-USDT")*0.95)
nbDePairesExecutionsPrecedentes=0
print(f"{str(datetime.now()).split('.')[0]} | Bot de sniping lancé avec {getSolde()} USDT, en attente de nouvelles paires...")
while True :
    #Récupération des données de kucoin
    liste_pairs = requests.get('https://openapi-v2.kucoin.com/api/v1/symbols').json()
    dataResponse = liste_pairs['data']
    df = pd.DataFrame(dataResponse, columns = ['symbol','enableTrading'])
    #df.drop(df.loc[df['enableTrading']==False].index, inplace=True)
    df = df[df.symbol.str.contains("-USDT")]

    #On créer une liste avec le nom de paires
    perpListBase = []
    for index, row in df.iterrows():
        perpListBase.append(row['symbol'])
    #On vérifie que le nombre de paires de notre dernière execution est identique.
    #Si une nouvelle paire existe
    if len(perpListBase) > nbDePairesExecutionsPrecedentes and nbDePairesExecutionsPrecedentes!=0:
        print(f"{str(datetime.now()).split('.')[0]} | Nouvelle paire disponible !!!")
        #On compare nos 2 listes pour récupérer le nom de la nouvelle paire
        symbol=''
        for pair in perpListBase:
            if pair not in perpListEx :
                symbol=pair
        if symbol != '' :
            print(f"{str(datetime.now()).split('.')[0]} | Tentative de snipping sur {symbol} avec {getSolde()} USDT")
            amount = getSolde()/getCurrentPrice(symbol)*0.95
            seconds_before_sell = 10

            while True:
                try:
                    kucoin.reload_markets()
                    kucoin.place_market_order(symbol, "buy", amount)
                    print(f"{str(datetime.now()).split('.')[0]} | Buy Order success!")

                    print(f"{str(datetime.now()).split('.')[0]} | Waiting for sell...")
                    time.sleep(seconds_before_sell)

                    kucoin.place_market_order(symbol, "sell", amount)
                    print(f"{str(datetime.now()).split('.')[0]} | Sell Order success!")

                    break
                except Exception as err:
                    print(err)
                    if str(err) == "kucoin does not have market symbol " + symbol:
                        time.sleep(0.1)
                    else :
                        print(err)
                    pass
            print(f"{str(datetime.now()).split('.')[0]} | Sniping réalisé sur {symbol}")
            del symbol
        else :
            print(f"{str(datetime.now()).split('.')[0]} | Aucune paire n'est différente entre cette execution et l'execution précedente")
            print(f"symbol={symbol}")
        #On sauvegarde ce nombre pour le vérifier juste après
        nbDePairesExecutionsPrecedentes=len(perpListBase)
        #On sauvegarde l'ancienne liste
        perpListEx=perpListBase
    #Si le nombre de paires est toujours le même :
    else :
        #On sauvegarde ce nombre pour le vérifier juste après
        nbDePairesExecutionsPrecedentes=len(perpListBase)
        #On sauvegarde l'ancienne liste
        perpListEx=perpListBase
        #Pour afficher un message toutes les heures dans la console:
        now = datetime.now()
        minute0=int(now.strftime("%M"))+int(now.strftime("%S"))
        if minute0==0:
            #print(f"{str(datetime.now()).split('.')[0]} | Bot-snip toujours en cours d'execution : Aucune nouvelle paire : {len(perpListBase)} paires disponibles")
            pass
