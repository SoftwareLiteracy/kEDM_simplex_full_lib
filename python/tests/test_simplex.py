import kedm
import numpy as np
import pytest


@pytest.mark.parametrize("E", range(2, 6))
def test_simplex(pytestconfig, E):
    tau, Tp = 1, 1

    ts = np.loadtxt(pytestconfig.rootdir / "test/simplex_test_data.csv",
                    skiprows=1)
    valid = np.loadtxt(pytestconfig.rootdir / f"test/simplex_test_validation_E{E}.csv",
                       skiprows=1)

    library = ts[:len(ts)//2]
    target = ts[len(ts)//2-(E-1)*tau:len(ts)-(E-1)*tau]

    prediction = kedm.simplex(library, target, E, tau, Tp)

    assert prediction == pytest.approx(valid, abs=1e-2)


def test_multivariate_simplex(pytestconfig):
    E, tau, Tp = 3, 1, 1

    data = np.loadtxt(pytestconfig.rootdir / "test/block_3sp.csv", skiprows=1,
                      delimiter=",")
    valid = np.loadtxt(pytestconfig.rootdir / "test/block_3sp_validation.csv",
                       skiprows=1, delimiter=",")

    # Columns #1, #4 and #7 are x_t, y_t and z_t
    library = data[:99, [1, 4, 7]]
    target = data[97:198, [1, 4, 7]]

    prediction = kedm.simplex(library, target, E, tau, Tp)

    assert prediction[:, 0] == pytest.approx(valid, abs=1e-6)


@pytest.mark.parametrize("E", range(1, 21))
def test_simplex_rho(pytestconfig, E):
    tau, Tp = 1, 1

    ts = np.loadtxt(pytestconfig.rootdir / "test/TentMap_rEDM.csv",
                    delimiter=",", skiprows=1, usecols=1)
    valid = np.loadtxt(pytestconfig.rootdir / "test/TentMap_rEDM_validation.csv",
                       delimiter=",", skiprows=1, usecols=1)

    library = ts[0:100]
    target = ts[200 - (E - 1) * tau:500]
    prediction = kedm.simplex(library, target, E, tau, Tp)

    rho = np.corrcoef(prediction[:-1], target[(E-1)*tau+Tp:])[0][1]
    rho_valid = valid[E-1]

    assert rho == pytest.approx(rho_valid, abs=1e-6)

    rho = kedm.eval_simplex(library, target, E, tau, Tp)

    assert rho == pytest.approx(rho_valid, abs=1e-6)


def test_invalid_args():
    library = np.random.rand(10)
    target = np.random.rand(10)

    with pytest.raises(ValueError, match=r"E must be greater than zero"):
        kedm.simplex(library, target, E=-1)

    with pytest.raises(ValueError, match=r"tau must be greater than zero"):
        kedm.simplex(library, target, E=2, tau=-1)

    with pytest.raises(ValueError, match=r"Tp must be greater or equal to zero"):
        kedm.simplex(library, target, E=2, tau=1, Tp=-1)

    with pytest.raises(ValueError, match=r"library size is too small"):
        kedm.simplex(np.random.rand(1), target)

    with pytest.raises(ValueError, match=r"target size is too small"):
        kedm.simplex(library, np.random.rand(1), E=2)

    with pytest.raises(ValueError, match=r"library and target must have same"
                                         r" dimensionality"):
        kedm.simplex(np.random.rand(10), np.random.rand(10, 2))

    with pytest.raises(ValueError, match=r"library and target must be 1D or 2D"
                                         r" arrays"):
        kedm.simplex(np.random.rand(10, 2, 3), np.random.rand(10, 3, 4))
