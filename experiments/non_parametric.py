from jax.experimental.stax import Dense, Dropout, Tanh, Relu, randn
from jax.experimental import optimizers

import lifelike.losses as losses
from lifelike import Model
from lifelike.callbacks import *


def get_colon_dataset():
    import pandas as pd
    from patsy import dmatrix

    df = pd.read_csv("experiments/colon.csv", index_col=0).dropna()

    model_string = """{extent} +
        {rx} +
        {differ} +
        sex + age + obstruct + perfor + adhere + nodes + node4 + surg +
        time + status""".format(
        rx="C(rx, Treatment('Obs'))",
        differ="C(differ, Treatment(1))",
        extent="C(extent, Treatment(1))",
    )
    df = dmatrix(model_string, df, return_type="dataframe")

    T_train = df.pop("time").values
    E_train = df.pop("status").values
    X_train = df.values

    return X_train, T_train, E_train


def get_rossi_dataset():
    from lifelines.datasets import load_rossi

    df = load_rossi()

    T_train = df.pop("week").values
    E_train = df.pop("arrest").values
    X_train = df.values

    return X_train, T_train, E_train


x_train, t_train, e_train = get_colon_dataset()


model = Model([Dense(18), Relu])

model.compile(
    optimizer=optimizers.adam,
    optimizer_kwargs={"step_size": 0.001},
    loss=losses.NonParametric(),
)

model.fit(
    x_train,
    t_train,
    e_train,
    epochs=100000,
    batch_size=100,
    callbacks=[
        Logger(report_every_n_epochs=50),
        EarlyStopping(rdelta=1),
        TerminateOnNaN(),
        ModelCheckpoint("testsavefile.pickle", prefix_timestamp=False, save_every_n_epochs=200)
    ],
)
