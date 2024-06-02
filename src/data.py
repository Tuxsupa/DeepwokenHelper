import re
import json
import requests


class DeepwokenData():
    def __init__(self, buildId: str):
        self.build = self.getData(f'https://api.deepwoken.co/build?id={buildId}')
        self.talents = self.build.get('talents', [])
        self.mantras = self.build.get('mantras', [])
        self.stats = self.build['stats']
        self.traits = self.stats['traits']
        
        self.attributes:dict = self.build['attributes']
        self.preShrine = {category: {sub_category: 0 for sub_category in attributes} for category, attributes in self.attributes.items()}
        self.preShrine.update(self.build.get('preShrine', {}))

        with open('./assets/races.json') as f:
            racesJson = json.load(f)
            
        self.racialStats = {
			"Strength": 0,
			"Fortitude": 0,
			"Agility": 0,
			"Intelligence": 0,
			"Willpower": 0,
			"Charisma": 0
		}
        self.racialStats.update(racesJson["racesStats"][self.build["stats"]["meta"]["Race"]])

        self.all_talents = self.getData('https://api.deepwoken.co/get?type=talent&name=all')
        self.all_mantras = self.getData('https://api.deepwoken.co/get?type=mantra&name=all')
        
        Talents(self)
        Mantras(self)
        
        self.all_talents['Fold'] = {}
        self.all_mantras['Mystery Mantra'] = {}
        self.all_mantras['Roll 2'] = {}

        self.all_strings = list(self.all_talents.keys()) + list(self.all_mantras.keys()) + list(self.traits.keys())
    
    @staticmethod
    def getData(url):
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()['content']
        else:
            print("Failed to fetch the web page. Status code: ", response.status_code)
    

class Talents():
    def __init__(self, data: DeepwokenData):
        self.data = data
        self.update_talents()

    def check_reqs(self, type, talent):
        for req_type, req_value in talent["reqs"].items():
            if type == "normal":
                if talent["name"] == "Neuroplasticity":
                    if (
                        self.data.attributes["base"]["Willpower"] >= 35
                        or self.data.attributes["base"]["Intelligence"] >= 35
                        or self.data.attributes["base"]["Charisma"] >= 35
                    ):
                        return True
            else:
                if self.data.preShrine is None:
                    return False

                if talent["name"] == "Neuroplasticity":
                    if (
                        self.data.preShrine["base"]["Willpower"] + self.data.racialStats["Willpower"] >= 35
                        or self.data.preShrine["base"]["Intelligence"] + self.data.racialStats["Intelligence"] >= 35
                        or self.data.preShrine["base"]["Charisma"] + self.data.racialStats["Charisma"] >= 35
                    ):
                        return True

            if isinstance(req_value, dict):
                for req, value in req_value.items():
                    if type == "normal":
                        if self.data.attributes[req_type][req] < value:
                            return False
                    else:
                        if self.data.preShrine is None:
                            return False
                        racial = self.data.racialStats.get(req, 0)
                        if self.data.preShrine[req_type].get(req, 0) + racial < value:
                            return False

        if talent["reqs"]["from"] == "":
            return True

        for pre_req in talent["reqs"]["from"].split(", "):
            if pre_req.lower() not in self.data.all_talents:
                return True

            if not self.check_reqs("normal", self.data.all_talents[pre_req.lower()]):
                if not self.check_reqs("shrine", self.data.all_talents[pre_req.lower()]):
                    return False

        return True
    
    def update_talents(self):        
        if not self.data.stats:
            return
        
        blacklist = {
            "categories": ['Innate', 'Angler', 'Shipwright', 'Deepwoken'],
            "talents": ['Blinded'],
            "rarities": ['Origin', 'Outfit', 'Unique', 'Equipment']
        }
        
        same_differences = {}
        
        for talent_name, talent in self.data.all_talents.items():
            if talent["rarity"] in blacklist["rarities"]:
                continue
            if talent["category"] in blacklist["categories"]:
                continue
            if talent_name in blacklist["talents"]:
                continue

            talent["shrine"] = False
            talent["taken"] = False
            talent["forTaken"] = []
            talent["shrineTaken"] = False
            
            if not self.check_reqs('normal', talent):
                if not self.check_reqs('shrine', talent):
                    continue
                talent["shrine"] = True
            
            
            if talent["name"] in self.data.talents:
                talent["taken"] = True
            
            
            talent_name = re.sub(r' \[[A-Za-z]{3}\]', '', talent_name)
            for exclusive in talent["exclusiveWith"]:
                other_name = re.sub(r' \[[A-Za-z]{3}\]', '', exclusive.lower())
                
                if talent_name == other_name:
                    if talent_name not in same_differences:
                        same_differences[talent_name] = [talent["name"]]
                    
                    if exclusive not in same_differences[talent_name]:
                        same_differences[talent_name].append(exclusive)
        
        for talent_name in self.data.talents:
            talent = self.data.all_talents.get(talent_name.lower())
            if not talent: 
                continue
            
            if talent["reqs"]["from"] != "":
                for req in talent["reqs"]["from"].split(", "):
                    if req.lower() not in self.data.all_talents:
                        continue

                    card = self.data.all_talents[req.lower()]
                    card["forTaken"].append(talent["name"])
                    
                    if talent["shrine"]:
                        card["shrineTaken"] = True
        
        
        for talent_name, diff in same_differences.items():
            new_data = {}
            new_reqs = {}
            differences = {}
            for diff_name in diff:
                data = self.data.all_talents[diff_name.lower()]
                
                if not new_reqs:
                    new_reqs = data["reqs"]
                
                
                for type, value in data['reqs'].items():
                    if isinstance(value, dict):
                        for req_key, req_value in value.items():
                            if new_reqs[type][req_key] != req_value:
                                if req_value > 0:
                                    differences[req_key] = req_value
                                if new_reqs[type][req_key] > 0:
                                    differences[req_key] = new_reqs[type][req_key]
                
            
                if data["taken"]:
                    new_data = data
                    
                self.data.all_talents.pop(diff_name.lower(), None)

            if not new_data:
                new_data = data
            new_data["name"] = re.sub(r' \[[A-Za-z]{3}\]', '', new_data["name"])

            for type, value in new_data['reqs'].items():
                if isinstance(value, dict):
                    for req_key, req_value in value.items():
                        if req_key in differences:
                            new_data['reqs'][type][req_key] = 0
            
            new_data["diffReqs"] = differences
            new_data["exclusiveWith"] = [item for item in new_data["exclusiveWith"] if item not in same_differences[talent_name]]
            self.data.all_talents[talent_name] = new_data


class Mantras():
    def __init__(self, data: DeepwokenData):
        self.data = data
        self.update_mantras()
        
    def check_reqs(self, type, talent):
        for req_type, req_value in talent['reqs'].items():
            if isinstance(req_value, dict):
                for req, value in req_value.items():
                    if type == "normal":
                        if req_type == "from":
                            continue
                        if self.data.attributes[req_type][req] < value:
                            return False
                    else:
                        if self.data.preShrine is None:
                            return False
                        racial = self.data.racialStats.get(req, 0)
                        if self.data.preShrine[req_type].get(req, 0) + racial < value:
                            return False
        return True

    def update_mantras(self):
        if not self.data.stats:
            return

        for mantra_name, mantra in self.data.all_mantras.items():
            mantra['shrine'] = False
            mantra["taken"] = False

            if not self.check_reqs("normal", mantra):
                if not self.check_reqs("shrine", mantra):
                    continue
                mantra['shrine'] = True


            if mantra["name"] in self.data.mantras:
                mantra["taken"] = True

if __name__ == '__main__':
    DeepwokenData()
