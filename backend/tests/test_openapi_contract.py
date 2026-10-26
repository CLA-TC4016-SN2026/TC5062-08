from pathlib import Path

import yaml

from src.main import API_PREFIX, app


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


def test_api_does_not_advertise_bearer_security() -> None:
    served_contract = app.openapi()
    assert "security" not in served_contract
    assert "bearerAuth" not in served_contract.get("components", {}).get("securitySchemes", {})
