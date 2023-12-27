# NOTE: must enable feature in admin panel first
from roboflow import Roboflow
rf = Roboflow(api_key="API")
project = rf.workspace().project("PROJECT-ID")
model = project.version(1).model

model.download()
