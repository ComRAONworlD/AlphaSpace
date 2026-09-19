import numpy as np
import scipy.stats as stats
from knowledge_base import DISTRIBUTION_KNOWLEDGE

DISTRIBUTIONS = {
    "continuous": {
        "norm": {
            "name": "정규분포 (Normal)",
            "func": stats.norm,
            "params": [("평균 (μ)", "0", -20.0, 20.0, 0.5, False), ("표준편차 (σ)", "1", 0.1, 10.0, 0.1, False)]
        },
        "lognorm": {
            "name": "로그정규분포 (Lognormal)",
            "func": stats.lognorm,
            "params": [("로그평균 (μ)", "0", -5.0, 5.0, 0.2, False), ("로그표준편차 (σ)", "0.8", 0.05, 3.0, 0.05, False)]
        },
        "t": {
            "name": "t-분포 (Student's t)",
            "func": stats.t,
            "params": [("자유도 (v)", "10", 1.0, 100.0, 1.0, True), ("위치 (μ)", "0", -10.0, 10.0, 0.5, False), ("척도 (σ)", "1", 0.1, 5.0, 0.1, False)]
        },
        "chi2": {
            "name": "카이제곱분포 (Chi-squared)",
            "func": stats.chi2,
            "params": [("자유도 (k)", "5", 1.0, 50.0, 1.0, True)]
        },
        "f": {
            "name": "F-분포 (F)",
            "func": stats.f,
            "params": [("자유도1 (d1)", "5", 1.0, 50.0, 1.0, True), ("자유도2 (d2)", "10", 1.0, 100.0, 1.0, True)]
        },
        "expon": {
            "name": "지수분포 (Exponential)",
            "func": stats.expon,
            "params": [("발생률 (λ)", "1", 0.1, 10.0, 0.1, False)]
        }, 
        "gamma": {
            "name": "감마분포 (Gamma)",
            "func": stats.gamma,
            "params": [("형태 (α, k)", "2", 0.2, 15.0, 0.2, False), ("척도 (θ)=1/β", "1", 0.1, 10.0, 0.1, False)]
        },
        "weibull_min": {
            "name": "와이불분포 (Weibull)",
            "func": stats.weibull_min,
            "params": [("형태 (k)", "1.5", 0.2, 10.0, 0.1, False), ("척도 (λ)", "1", 0.1, 10.0, 0.2, False)]
        },
        "uniform": {
            "name": "균일분포 (Uniform)",
            "func": stats.uniform,
            "params": [("최소 (a)", "0", -20.0, 20.0, 1.0, False), ("최대 (b)", "1", -10.0, 30.0, 1.0, False)]
        },
        "beta": {
            "name": "베타분포 (Beta)",
            "func": stats.beta,
            "params": [("형태1 (α)", "2", 0.2, 15.0, 0.2, False), ("형태2 (β)", "5", 0.2, 15.0, 0.2, False)]
        },
        "cauchy": {
            "name": "코시분포 (Cauchy)",
            "func": stats.cauchy,
            "params": [("위치 (x₀)", "0", -10.0, 10.0, 0.5, False), ("척도 (γ)", "1", 0.1, 10.0, 0.2, False)]
        },
        "laplace": {
            "name": "라플라스분포 (Laplace)",
            "func": stats.laplace,
            "params": [("위치 (μ)", "0", -10.0, 10.0, 0.5, False), ("척도 (b)", "1", 0.1, 5.0, 0.1, False)]
        },
        "logistic": {
            "name": "로지스틱분포 (Logistic)",
            "func": stats.logistic,
            "params": [("위치 (μ)", "0", -10.0, 10.0, 0.5, False), ("척도 (s)", "1", 0.1, 5.0, 0.1, False)]
        },
        "pareto": {
            "name": "파레토분포 (Pareto)",
            "func": stats.pareto,
            "params": [("형태 (α)", "3", 0.5, 10.0, 0.2, False), ("척도 (x_m)", "1", 0.1, 10.0, 0.2, False)]
        },
        "rayleigh": {
            "name": "레일리분포 (Rayleigh)",
            "func": stats.rayleigh,
            "params": [("척도 (σ)", "1", 0.1, 10.0, 0.2, False)]
        },
    },
    "discrete": {
        "binom": {
            "name": "이항분포 (Binomial)",
            "func": stats.binom,
            "params": [("시행 횟수 (n)", "10", 1.0, 100.0, 1.0, True), ("성공 확률 (p)", "0.5", 0.01, 0.99, 0.05, False)]
        },
        "poisson": {
            "name": "포아송분포 (Poisson)",
            "func": stats.poisson,
            "params": [("발생률 (λ)", "3", 0.1, 30.0, 0.5, False)]
        },
        "geom": {
            "name": "기하분포 (첫 성공 시도횟수, X≥1)",
            "func": stats.geom,
            "params": [("성공 확률 (p)", "0.5", 0.05, 0.95, 0.05, False)]
        },
        "hypergeom": {
            "name": "초기하분포 (Hypergeom)",
            "func": stats.hypergeom,
            "params": [("모집단 크기 (N)", "20", 5.0, 100.0, 1.0, True), ("모집단 내 성공수 (K)", "7", 1.0, 50.0, 1.0, True), ("추출 횟수 (n)", "12", 1.0, 50.0, 1.0, True)]
        },
        "nbinom": {
            "name": "음이항분포 (성공 전 실패횟수, X≥0)",
            "func": stats.nbinom,
            "params": [("목표 성공 횟수 (r)", "5", 1.0, 50.0, 1.0, True), ("성공 확률 (p)", "0.5", 0.05, 0.95, 0.05, False)]
        },
        "randint": {
            "name": "이산균일분포 (Discrete Uniform)",
            "func": stats.randint,
            "params": [("최소 (a)", "1", -20.0, 20.0, 1.0, True), ("최대 (b)", "6", -10.0, 30.0, 1.0, True)]
        }, 
    }
}

def map_params(d_type, dist_key, raw_params):
    args, kwargs = [], {}
    if dist_key == "norm":
        kwargs = {"loc": raw_params[0], "scale": raw_params[1]}
    elif dist_key == "lognorm":
        args, kwargs = [raw_params[1]], {"scale": np.exp(raw_params[0])}
    elif dist_key == "t":
        args, kwargs = [raw_params[0]], {"loc": raw_params[1], "scale": raw_params[2]}
    elif dist_key == "chi2":
        args = [raw_params[0]]
    elif dist_key == "f":
        args = [raw_params[0], raw_params[1]]
    elif dist_key == "expon":
        kwargs = {"scale": 1.0 / raw_params[0] if raw_params[0] > 0 else 1.0}
    elif dist_key == "gamma":
        args, kwargs = [raw_params[0]], {"scale": raw_params[1]}
    elif dist_key == "weibull_min":
        args, kwargs = [raw_params[0]], {"scale": raw_params[1]}
    elif dist_key == "uniform":
        # 최소 a, 최대 b
        loc = raw_params[0]
        scale = max(raw_params[1] - raw_params[0], 1e-4)
        kwargs = {"loc": loc, "scale": scale}
    elif dist_key == "beta":
        args = [raw_params[0], raw_params[1]]
    elif dist_key == "cauchy":
        kwargs = {"loc": raw_params[0], "scale": raw_params[1]}
    elif dist_key == "laplace":
        kwargs = {"loc": raw_params[0], "scale": raw_params[1]}
    elif dist_key == "logistic":
        kwargs = {"loc": raw_params[0], "scale": raw_params[1]}
    elif dist_key == "pareto":
        args, kwargs = [raw_params[0]], {"scale": raw_params[1]}
    elif dist_key == "rayleigh":
        kwargs = {"scale": raw_params[0]}
    elif dist_key == "binom":
        args = [int(raw_params[0]), raw_params[1]]
    elif dist_key == "poisson":
        args = [raw_params[0]]
    elif dist_key == "geom":
        args = [raw_params[0]]
    elif dist_key == "hypergeom":
        N = int(raw_params[0])
        K = min(int(raw_params[1]), N)
        n = min(int(raw_params[2]), N)
        args = [N, K, n]
    elif dist_key == "nbinom":
        args = [int(raw_params[0]), raw_params[1]]
    elif dist_key == "randint":
        a = int(raw_params[0])
        b = max(int(raw_params[1]), a)
        args = [a, b + 1]
    return args, kwargs

def calculate_theoretical_stats(dist_instance, dist_key):
    """
    분포 인스턴스로부터 이론적 통계량(평균, 분산, 표준편차, 왜도, 첨도, 중앙값)을 안전하게 계산
    """
    stats_dict = {}
    
    if dist_key == "cauchy":
        stats_dict["mean"] = "존재하지 않음 (Undefined)"
        stats_dict["var"] = "무한대 (∞)"
        stats_dict["std"] = "무한대 (∞)"
        stats_dict["skew"] = "존재하지 않음"
        stats_dict["kurt"] = "존재하지 않음"
        try:
            stats_dict["median"] = f"{dist_instance.median():.4f}"
        except:
            stats_dict["median"] = "-"
        return stats_dict

    try:
        m, v, s, k = dist_instance.stats(moments='mvsk')
        
        # Mean
        if np.isnan(m) or np.isinf(m):
            stats_dict["mean"] = "수렴하지 않음 (Undefined)"
        else:
            stats_dict["mean"] = f"{float(m):.4f}"
            
        # Variance & Std Dev
        if np.isnan(v) or np.isinf(v):
            stats_dict["var"] = "무한대 (∞)"
            stats_dict["std"] = "무한대 (∞)"
        else:
            stats_dict["var"] = f"{float(v):.4f}"
            stats_dict["std"] = f"{np.sqrt(float(v)):.4f}"
            
        # Skewness
        if np.isnan(s) or np.isinf(s):
            stats_dict["skew"] = "정의 불가"
        else:
            stats_dict["skew"] = f"{float(s):.4f}"
            
        # Kurtosis
        if np.isnan(k) or np.isinf(k):
            stats_dict["kurt"] = "정의 불가"
        else:
            stats_dict["kurt"] = f"{float(k):.4f}"
            
        # Median
        try:
            med = dist_instance.median()
            stats_dict["median"] = f"{float(med):.4f}" if isinstance(med, (int, float, np.number)) else "-"
        except:
            stats_dict["median"] = "-"
            
    except Exception as e:
        stats_dict["mean"] = "-"
        stats_dict["var"] = "-"
        stats_dict["std"] = "-"
        stats_dict["skew"] = "-"
        stats_dict["kurt"] = "-"
        stats_dict["median"] = "-"

    return stats_dict
