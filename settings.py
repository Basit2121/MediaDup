import json

settings = open('settings.json','w+')
settingsd={}
rel = (int(input("Please input how many random effects should be added (INTEGER only)\n")));vidc = (int(input("Please input how many unicalizations should be done to the video(INTEGER only) (How many videos to make)\n")));mind = (int(input("Please input minimum video length(INTEGER only)\n")));maxd = (int(input("Please input maximum video length(INTEGER only)\n")));doMirror = bool(int(input("Enable mirroring? (1 - yes, 0 - no)\n")));showEffect = bool(int(input("Enable fade-in effect? (1 - yes, 0 - no)\n")));doRotate = bool(int(input("Enable rotation effect? (1 - yes, 0 - no)\n")));doblur = bool(int(input("Enable blur? (1 - yes, 0 - no)\n")));doBlurIn = bool(int(input("Enable blur-in effect? (1 - yes, 0 - no)\n")))
if doblur or doBlurIn:
	blursigma = (int(input("Input blur depth, in px, integer only.\n")))
else:
	blursigma = 0
settingsd['rel']=rel;settingsd['vidc']=vidc;settingsd['mind']=mind;settingsd['maxd']=maxd;settingsd['doMirror']=doMirror;settingsd['showEffect']=showEffect;settingsd['doRotate']=doRotate;settingsd['doblur']=doblur;settingsd['blursigma']=blursigma;settingsd['doBlurIn']=doBlurIn
settings.write(json.dumps(settingsd))
settings.close()
print('Settings successfully saved!')