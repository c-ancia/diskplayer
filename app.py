import os
from subprocess import run, PIPE
from flask import Flask, render_template, flash, redirect, url_for, request
from src.recorder import Recorder
from webapp.forms.overrideform import OverrideForm
from webapp.forms.recorderform import RecorderForm
from src.player import Player
from src.recorder import Recorder

project_dir = (os.path.sep).join(os.path.abspath(__file__).split(os.path.sep)[:-1])
template_dir = os.path.join(project_dir, (os.path.sep).join(("webapp", "templates")))
app = Flask(__name__, template_folder=template_dir)
app.config.from_json(f"{project_dir}{os.path.sep}resources/config.json")

def get_floppy():
    output = run("lsblk -o name -l", shell=True, stdout=PIPE)
    lsblk = output.stdout.decode('utf-8')
    lsblk = lsblk.strip()
    lsblk = lsblk.split('\n')
    return lsblk[1]


@app.route('/', methods=['GET','POST'])
def index():
    overrideform = OverrideForm()
    override = None
    hasContent = None
    currentContent = None
    
    # Check if floppy exists
    lsblk = get_floppy()
    
    # Check if the floppy has content
    if lsblk == "sda":
        rec = Recorder(path="/media/floppy/diskplayer.contents")
        hasContent = rec.file_exists()
        if hasContent == False:
            return redirect(url_for('record'))
        else:
            # Get current playback
            pla = Player(f"{project_dir}{os.path.sep}resources/config.json")
            currentContent = pla.getCurrentPlayback()
    
    # Check if the user decided to override the floppy or not
    if overrideform.validate_on_submit():
        formdata = request.form
        override = formdata["override"]
        if override == "1":
            return redirect(url_for('record', override=override))

    return render_template('index.html', lsblk=lsblk, hasContent=hasContent, currentContent=currentContent, override=override, overrideform=overrideform)

@app.route('/record', methods=['GET','POST'])
def record():
    recorderform = RecorderForm()
    override = request.args.get('override')
    noContent = override == None
    
    # Check if floppy exists
    lsblk = get_floppy()
    
    # Check user input and records file
    if recorderform.validate_on_submit():
        formdata = request.form
        filepath = f"{project_dir}{os.path.sep}tmp{os.path.sep}diskplayer.contents"
        rec = Recorder(path=filepath, uri=formdata["uri"])
        result = rec.record()
        if result["error"]:
            return redirect(url_for('result', error=result["error"], message=result["message"]))
        else:
            return redirect(url_for('result', error=result["error"]))
       
    return render_template('recorderform.html', lsblk=lsblk, noContent=noContent, recorderform=recorderform )


@app.route('/result')
def result():
    error = request.args.get('error')
    message = request.args.get('message')
    return render_template('result.html', error=error, message=message)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4871)