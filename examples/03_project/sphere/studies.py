from pyvicar.tools.study import StudyType
import params

# studies.py is the 2nd node following params.py
# a study is a concise code that can be easily typed to generate or refer to a params struct
# it may seem unnecessary to name and manage a params struct
# but it becomes inevitable starting to manage complex parameter space
# especially trying to maximize inspection and postprocessing efficiency


# StudyType defines the coding standard of a parameter space (a frame)
# StudyVal is a specific study in the parameter space (a coordinate)
# in this example, the code looks like 're1000dev', 're1000recr120', 're1000devre120t'
def make_study_t():
    return (
        StudyType()
        .add_int("re", "re")
        .add_choice("stage", "", ("dev", "rec"))
        .add_optional_int("resolution", "r", off_value=20)  # set value=20 if not active
        .add_switch("step_test", "t")
    )
    # specify dev to run with few dumps for a long time to let the flow first develop
    # specify rec to run for short time and frequent dumps to record vortices
    # rename the folders to remove d after developing stage is completed and start as a new code
    # using different names prevents confusions on the simulation stages when running batches

    # if resolution is not specified, make a lightweight test


def to_params(code):
    study_t = make_study_t()
    study = study_t.decode(code)

    return params.make_params(
        name=study.encode(),
        re=study.re.value,
        d_by_dx=study.resolution.value,
        gcss="gcm" if study.resolution.on else "ssm",
        stage=study.stage.choice,
        step_test=study.step_test.on,
        body_test=not study.resolution.on,
    )
