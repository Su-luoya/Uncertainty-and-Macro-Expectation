class ProjectPath:
    # & Data
    data: str = "data"
    raw: str = f"{data}/raw"
    derived: str = f"{data}/derived"
    individual_reg: str = f"{derived}/individual"
    consensus_reg: str = f"{derived}/consensus"
    beta_reg: str = f"{derived}/beta"

    survey: str = f"{raw}/Survey"
    # individual: str = f"{survey}/Individual"
    # consensus: str = f"{survey}/Consensus"
    real: str = f"{raw}/Real"
    uncertainty: str = f"{raw}/Uncertainty"

    # & Cache
    cache: str = "cache"
