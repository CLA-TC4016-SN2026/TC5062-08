from pathlib import Path

import yaml

from src.auth import get_current_account
from src.main import API_PREFIX, app

PUBLIC_OPERATIONS = {
    "registrarCuenta",
    "verificarCorreo",
    "solicitarDesafioCodigo",
    "crearSesion",
    "solicitarRecuperacion",
    "restablecerContrasena",
}


def _find_repo_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("Could not locate repository root (no .git found above tests/).")


_REPO_ROOT = _find_repo_root(Path(__file__).resolve())
CONTRACT_PATH = _REPO_ROOT / "S05_S06_A1" / "S04_A3" / "openapi_equipo.yaml"
if not CONTRACT_PATH.exists():
    CONTRACT_PATH = _REPO_ROOT / "S05_S06_A1" / "openapi_equipo.yaml"


def test_routes_and_methods_match_team_contract() -> None:
    contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    expected = {
        (path, method.upper(), operation["operationId"])
        for path, path_item in contract["paths"].items()
        for method, operation in path_item.items()
        if method in {"get", "post", "put", "patch", "delete"}
    }
    actual = {
        (
            route.path.removeprefix(API_PREFIX),
            method,
            route.operation_id,
        )
        for route in app.routes
        if getattr(route, "operation_id", None)
        and route.path != f"{API_PREFIX}/health"
        for method in route.methods or set()
        if method in {"GET", "POST", "PUT", "PATCH", "DELETE"}
    }
    assert actual == expected


def test_success_status_codes_match_team_contract() -> None:
    contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    routes = {
        (route.path.removeprefix(API_PREFIX), method): route
        for route in app.routes
        if getattr(route, "operation_id", None)
        and route.path != f"{API_PREFIX}/health"
        for method in route.methods or set()
        if method in {"GET", "POST", "PUT", "PATCH", "DELETE"}
    }
    for path, path_item in contract["paths"].items():
        for method, operation in path_item.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            route = routes[(path, method.upper())]
            declared_success = {
                int(code)
                for code in operation["responses"]
                if code.startswith("2")
            }
            assert declared_success == {route.status_code or 200}


def test_api_advertises_bearer_security() -> None:
    served_contract = app.openapi()
    assert served_contract.get("security") == [{"bearerAuth": []}]
    assert "bearerAuth" in served_contract.get("components", {}).get("securitySchemes", {})


def _all_dependency_calls(dependant) -> set:
    calls = {dependant.call} if dependant.call else set()
    for sub in dependant.dependencies:
        calls |= _all_dependency_calls(sub)
    return calls


def test_protected_routes_require_authentication() -> None:
    checked = 0
    for route in app.routes:
        operation_id = getattr(route, "operation_id", None)
        if not operation_id or route.path == f"{API_PREFIX}/health":
            continue
        checked += 1
        calls = _all_dependency_calls(route.dependant)
        if operation_id in PUBLIC_OPERATIONS:
            assert get_current_account not in calls, f"{operation_id} should stay public"
        else:
            assert get_current_account in calls, f"{operation_id} should require authentication"
    assert checked > len(PUBLIC_OPERATIONS)
