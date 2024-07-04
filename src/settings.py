class ProjectPath:
    # & Data
    data: str = "data"
    raw: str = f"{data}/raw"
    derived: str = f"{data}/derived"
    individual_reg: str = f"{derived}/disagreement/individual"
    consensus_reg: str = f"{derived}/disagreement/consensus"
    idio_reg: str = f"{derived}/disagreement/idiosyncratic"
    beta_reg: str = f"{derived}/beta"

    survey: str = f"{raw}/Survey Data"
    individual: str = f"{survey}/Individual"
    consensus: str = f"{survey}/Consensus"
    real: str = f"{raw}/Real-Time Data"
    uncertainty: str = f"{raw}/Uncertainty"

    # & Cache
    cache: str = "cache"
