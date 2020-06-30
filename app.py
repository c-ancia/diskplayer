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

config_path = f"{project_dir}{os.path.sep}resources/config.json"
media_filepath = f"{project_dir}{os.path.sep}media{os.path.sep}floppy{os.path.sep}diskplayer.contents"
tmp_filepath = f"{project_dir}{os.path.sep}tmp{os.path.sep}diskplayer.contents"

app = Flask(__name__, template_folder=template_dir)
app.config.from_json(config_path)

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
    has_content = None
    current_content = None

    # Check if floppy exists
    lsblk = get_floppy()

    # Check if the floppy has content
    if lsblk == "sda":
        rec = Recorder(path=media_filepath)
        has_content = rec.file_exists()
        if has_content == False:
            return redirect(url_for('record'))
        else:
            # Get current playback
            pla = Player(config_path)
            current_content = pla.get_current_playback()

    # Check if the user decided to override the floppy or not
    if overrideform.validate_on_submit():
        form_data = request.form
        override = form_data["override"]
        if override == "1":
            return redirect(url_for('record', override=override))

    return render_template('index.html', lsblk=lsblk, has_content=has_content, current_content=current_content, override=override, overrideform=overrideform)

@app.route('/record', methods=['GET','POST'])
def record():
    recorderform = RecorderForm()
    override = request.args.get('override')
    no_content = override == None

    # Check if floppy exists
    lsblk = get_floppy()

    # Check user input and records file
    if recorderform.validate_on_submit():
        form_data = request.form
        rec = Recorder(path=tmp_filepath, uri=form_data["uri"])
        result = rec.record()
        if result["error"]:
            return redirect(url_for('result', error=result["error"], message=result["message"]))
        else:
            return redirect(url_for('result', error=result["error"]))

    return render_template('recorderform.html', lsblk=lsblk, no_content=no_content, recorderform=recorderform )

@app.route('/result')
def result():
    error = request.args.get('error')
    message = request.args.get('message')
    return render_template('result.html', error=error, message=message)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4871)