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
        
        # filters = {
        #     "obtainables": {
        #         "PRE": { "name": 'PRE', "enabled": False },
        #         "POST": { "name": 'POST', "enabled": False },
        #         "FAV": { "name": 'FAV', "enabled": False },
        #         "STR": { "name": 'Strength', "enabled": False },
        #         "AGI": { "name": 'Agility', "enabled": False },
        #         "FTD": { "name": 'Fortitude', "enabled": False },
        #         "INT": { "name": 'Intelligence', "enabled": False },
        #         "WIL": { "name": 'Willpower', "enabled": False },
        #         "CHA": { "name": 'Charisma', "enabled": False }
        #     },
        #     "taken": {
        #         "PRE": { "name": 'PRE', "enabled": False },
        #         "POST": { "name": 'POST', "enabled": False },
        #         "FAV": { "name": 'FAV', "enabled": False },
        #         "STR": { "name": 'Strength', "enabled": False },
        #         "AGI": { "name": 'Agility', "enabled": False },
        #         "FTD": { "name": 'Fortitude', "enabled": False },
        #         "INT": { "name": 'Intelligence', "enabled": False },
        #         "WIL": { "name": 'Willpower', "enabled": False },
        #         "CHA": { "name": 'Charisma', "enabled": False }
        #     }
        # }
        
        # old_obtainables = obtainables.copy()
        # obtainables = {
        #     "Advanced": {},
        #     "Rare": {},
        #     "Common": {},
        #     "Oath": {},
        #     "Quest": {},
        #     "Murmur": {}
        # }
        
        # obtainables_talent_count = 0
        
        blacklist = {
            "categories": ['Innate', 'Angler', 'Shipwright', 'Deepwoken'],
            "talents": ['Blinded'],
            "rarities": ['Origin', 'Outfit', 'Unique', 'Equipment']
        }
        
        for talent_name, talent in self.data.all_talents.items():
            if talent["rarity"] in blacklist["rarities"]:
                continue
            if talent["category"] in blacklist["categories"]:
                continue
            if talent_name in blacklist["talents"]:
                continue
            
            talent["new"] = True
            talent["shrine"] = False
            talent["taken"] = False
            talent["forTaken"] = []
            # talent["locked"] = talent_name in locked_talents
            
            if not self.check_reqs('normal', talent):
                if not self.check_reqs('shrine', talent):
                    continue
                talent["shrine"] = True
                # print(talent_name)
            
            
            if talent["name"] in self.data.talents:
                talent["taken"] = True
            
            
            # for rarity, categories in old_obtainables.items():
            #     for category, old_talents in categories.items():
            #         for old_talent in old_talents:
            #             if talent_name == old_talent["name"]:
            #                 talent["new"] = False
            
            # if talent["rarity"] == "Oath":
            #     if self.data.stats["meta"]["Oath"] != talent["category"]:
            #         continue
            # elif talent["rarity"] == "Murmur":
            #     if self.data.stats["meta"]["Murmur"] != talent["reqs"]["from"]:
            #         continue
            
            # if talent["category"] == "Visionshaper":
            #     if self.data.stats["meta"]["Oath"] != "Visionshaper":
            #         continue
            
            # for filter_name, filter_data in filters["obtainables"].items():
            #     if filter_data["enabled"]:
            #         if filter_name in ['PRE', 'POST', 'FAV']:
            #             continue
            #         if talent["reqs"]["base"][filter_data["name"]] <= 0:
            #             continue
            
            # if filters["obtainables"]["PRE"]["enabled"] and not talent["shrine"]:
            #     continue
            # if filters["obtainables"]["POST"]["enabled"] and talent["shrine"]:
            #     continue
            # if filters["obtainables"]["FAV"]["enabled"] and not talent["loved"]:
            #     continue
            
            # if rollable_search.lower() in talent_name.lower() or rollable_search.lower() in talent["category"].lower():
            #     if talent["rarity"] not in obtainables or talent["category"] not in obtainables[talent["rarity"]]:
            #         obtainables[talent["rarity"]][talent["category"]] = []
            #     obtainables[talent["rarity"]][talent["category"]].append(talent)
            #     obtainables_talent_count += 1
        
        # for category, talents in taken_talents.items():
        #     for talent in talents:
        #         if self.check_reqs('normal', talent):
        #             talent["shrine"] = False
        #         elif self.check_reqs('shrine', talent):
        #             talent["shrine"] = True
        
        # for rarity, categories in obtainables.items():
        #     obtainables[rarity] = dict(sorted(categories.items()))
        #     for category, talents in obtainables[rarity].items():
        #         obtainables[rarity][category] = sorted(talents, key=lambda x: x["name"].lower())
        
        # taken_talents = dict(sorted(taken_talents.items()))
        # for category, talents in taken_talents.items():
        #     taken_talents[category] = sorted(talents, key=lambda x: x["name"].lower())
        
        # displayed_taken_talents = taken_talents.copy()
        # for category, talents in displayed_taken_talents.items():
        #     index = 0
        #     while index < len(talents):
        #         talent = talents[index]
        #         for filter_name, filter_data in filters["taken"].items():
        #             if filter_data["enabled"]:
        #                 if filter_name in ['PRE', 'POST', 'FAV']:
        #                     continue
        #                 if talent["reqs"]["base"][filter_data["name"]] <= 0:
        #                     talents.pop(index)
        #                     index -= 1
        #                     break
                
        #         if (filters["taken"]["PRE"]["enabled"] and not talent["shrine"]) or \
        #         (filters["taken"]["POST"]["enabled"] and talent["shrine"]) or \
        #         (filters["taken"]["FAV"]["enabled"] and not talent["loved"]):
        #             talents.pop(index)
        #             index -= 1
                
        #         index += 1
            
        #     if len(talents) == 0:
        #         del displayed_taken_talents[category]
        
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

        # info = oaths_data['info'].get(chosen_oath)
        # if info is None:
        #     return

        # for slot in mantra_slots:
        #     if info['slots'].get(slot) is not None:
        #         mantra_slots[slot] = base_mantra_slots[slot] + info['slots'][slot]
        #     else:
        #         mantra_slots[slot] = base_mantra_slots[slot]

        # if taken_talents_store is not None:
        #     if "Neuroplasticity" in taken_talents_store:
        #         mantra_slots['Wildcard'] += 1

        # obtainables = {
        #     "Combat": [],
        #     "Mobility": [],
        #     "Support": [],
        # }

        for mantra_name, mantra in self.data.all_mantras.items():
            mantra['shrine'] = False
            mantra["taken"] = False

            if not self.check_reqs("normal", mantra):
                if not self.check_reqs("shrine", mantra):
                    continue
                mantra['shrine'] = True
                # print(mantra_name)

            if mantra["name"] in self.data.mantras:
                mantra["taken"] = True

            # if mantra['type'] == "Oath":
            #     oath = mantra['reqs']['from'].split(": ")[1]
            #     if oath != self.data.stats['meta']['Oath']:
            #         continue

            # obtainables[mantra['category']].append(mantra)

        # mantra_mods = {}
        # for category, mantras in taken_mantras.items():
        #     for mantra in mantras:
        #         # Push to modifications table
        #         mantra_mods[mantra['name']] = {
        #             'gem': mantra['gem'],
        #             'spark': mantra['spark']
        #         }
        #     mantra_modifications.set(mantra_mods)

        # return obtainables

if __name__ == '__main__':
    DeepwokenData()
