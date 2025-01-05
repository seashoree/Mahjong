import urllib.parse
import urllib.request
import json
from tqdm import tqdm
import ssl

#hyperparameters2chose:
contest_list = ["","","","","",""]
save_file="./data/test.txt"


#readfile = "./matches/IJCAI2022.json"
#contest_id:616025ec5ddc087351c02fcb
headers = {'User-Agent':' Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
#with open(readfile,"r") as fread:

with open(save_file,"a") as fwrite:
    #7005局
    #while True:
    for contest_id in contest_list:
        contest_url = "https://botzone.org.cn/contest/display/gamecontest16?contest=" + contest_id
        req_contest = urllib.request.Request(contest_url,headers=headers)
        response_contest = urllib.request.urlopen(req_contest , context=ctx)
        data = json.loads(response_contest.read()) 
        #line = fread.readline()
        #if line is None:
        #    break
        #data = json.loads(line)
        match_list = data["contest"]["matches"]
        for i in tqdm(range(len(match_list)), desc='Processing'):
            match_id = match_list[i]["_id"]
            url = 'https://botzone.org.cn/match/'+match_id+'?lite=true'
            #https://botzone.org.cn/match/61602cb45ddc087351c04358?lite=true
            req = urllib.request.Request(url,headers=headers)
            response = urllib.request.urlopen(req, context=ctx)
            match_json = json.loads(response.read()) 

            match_quan = match_json["logs"][0]["output"]["display"]['quan']
            fwrite.write("Match "+match_id+"\n")
            fwrite.write("Wind "+str(match_quan)+"\n")

            match_tiles = match_json["logs"][2]["output"]["content"]
            for player in ['0', '1', '2', '3']:
                fwrite.write("Player "+player+" Deal"+match_tiles[player][9:]+"\n")
            
            #https://botzone.org.cn/match/62f3d1967c30dd3103abc99f
            #print(match_id)
            last_tile = ""
            last_player = ""
            for step in range(4, len(match_json["logs"]),2):
                display = match_json["logs"][step]["output"]["display"]
                
                if display["action"] == "DRAW":
                    player = display["player"]
                    fwrite.write("Player "+str(player)+" Draw "+display["tile"]+"\n")
                elif display["action"] == "PLAY":
                    player = display["player"]
                    fwrite.write("Player "+str(player)+" Play "+display["tile"]+"\n")
                else:
                    if display["action"] == "CHI":
                        player = display["player"]
                        fwrite.write("Player "+str(player)+" Chi "+display["tileCHI"])
                    elif display["action"] == "PENG":
                        player = display["player"]
                        fwrite.write("Player "+str(player)+" Peng "+last_tile)
                    elif display["action"] == "GANG":
                        player = display["player"]
                        if player != last_player:
                            fwrite.write("Player "+str(player)+" Gang "+display["tile"])
                        else:
                            fwrite.write("Player "+str(player)+" AnGang "+display["tile"])
                    elif display["action"] == "BUGANG":
                        player = display["player"]
                        fwrite.write("Player "+str(player)+" BuGang "+display["tile"])
                    elif display["action"] == "HU":
                        player = display["player"]
                        fwrite.write("Player "+str(player)+" Hu "+last_tile)
                    elif display["action"] == "HUANG":
                        fwrite.write("Huang\nScore 0 0 0 0")
                    else:
                        print("error: "+str(match_id))
                    
                    response = match_json["logs"][step-1]
                    for player_resp in [0,1,2,3]:
                        if player_resp!=player and response[str(player_resp)]["response"]!="PASS":
                            response_info = response[str(player_resp)]["response"].split(" ")
                            resp_act = response_info[0]
                            if resp_act == "CHI":
                                fwrite.write(" Ignore Player "+str(player_resp)+" Chi "+response_info[1])
                            elif resp_act == "PENG":
                                fwrite.write(" Ignore Player "+str(player_resp)+" Peng "+last_tile)
                            elif resp_act == "GANG":
                                if player_resp != last_player:
                                    fwrite.write(" Ignore Player "+str(player_resp)+" Gang "+last_tile)
                                else:
                                    fwrite.write(" Ignore Player "+str(player_resp)+" AnGang "+last_tile)
                            elif resp_act == "BUGANG":
                                fwrite.write(" Ignore Player "+str(player_resp)+" BuGang "+last_tile)
                            elif resp_act == "HU":
                                fwrite.write(" Ignore Player "+str(player_resp)+" Hu "+last_tile)
                    fwrite.write("\n")

                    if display["action"] == "CHI" or display["action"] == "PENG":
                        fwrite.write("Player "+str(player)+" Play "+display["tile"]+"\n")

                if display["action"] != "HUANG" and display["action"] != "HU" :
                    last_tile = display["tile"]
                    last_player = player

                if display["action"] == "HU":
                    fwrite.write("Fan "+str(display["fanCnt"])+" ")
                    for fan_id in range(len(display["fan"])):
                        if fan_id != len(display["fan"])-1:
                            fwrite.write(display["fan"][fan_id]["name"]+"*"+str(display["fan"][fan_id]["cnt"])+"+")
                        else:
                            fwrite.write(display["fan"][fan_id]["name"]+"*"+str(display["fan"][fan_id]["cnt"]))
                    fwrite.write("\n")
                    score = display["score"]
                    fwrite.write("Score "+str(score[0])+" "+str(score[1])+" "+str(score[2])+" "+str(score[3])+"\n")
            fwrite.write("\n")
            