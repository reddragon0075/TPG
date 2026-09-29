"""
Tests for Graph Traversal Engine — PRD-0002
"""

import pytest
from app.graph.traversal import GraphTraversalEngine
from app.models.entity import (
    Entity,
    EntityRelationship,
    EntityType,
    RelationshipType,
    ConfidenceLevel,
    EntityStatus,
)
from tests.conftest import TEST_WORKSPACE_ID


@pytest.mark.asyncio
async def test_subgraph_and_lineage_reconstruction(test_session):
    """
    Simulates the PRD-0001 benchmark:
    Client -> Problem -> Requirement -> Initiative (Vendor Wallet) -> Decision -> PRD -> KPI.
    Verifies that TPG traces the complete provenance tree.
    """
    ws_id = TEST_WORKSPACE_ID

    # 1. Create entities
    client = Entity(id="ent-client-1", workspace_id=ws_id, entity_type=EntityType.CUSTOMER, name="Acme Logistics")
    problem = Entity(id="ent-prob-1", workspace_id=ws_id, entity_type=EntityType.PROBLEM, name="Vendor Payment Reconciliation Delays")
    req = Entity(id="ent-req-1", workspace_id=ws_id, entity_type=EntityType.REQUIREMENT, name="Automated Batch Wallet Settlements")
    init = Entity(id="ent-init-1", workspace_id=ws_id, entity_type=EntityType.INITIATIVE, name="Vendor Wallet")
    dec = Entity(id="ent-dec-1", workspace_id=ws_id, entity_type=EntityType.DECISION, name="Approve Vendor Wallet MVP")
    prd = Entity(id="ent-prd-1", workspace_id=ws_id, entity_type=EntityType.PRD, name="PRD: Vendor Wallet v1")
    kpi = Entity(id="ent-kpi-1", workspace_id=ws_id, entity_type=EntityType.KPI, name="Reconciliation Time Reduced to < 2h")

    test_session.add_all([client, problem, req, init, dec, prd, kpi])
    await test_session.flush()

    # 2. Connect relationships
    # Client -> Problem
    r1 = EntityRelationship(source_entity_id=client.id, target_entity_id=problem.id, relationship_type=RelationshipType.CAUSED_BY)
    # Problem -> Req
    r2 = EntityRelationship(source_entity_id=problem.id, target_entity_id=req.id, relationship_type=RelationshipType.SUPPORTS)
    # Req -> Init
    r3 = EntityRelationship(source_entity_id=req.id, target_entity_id=init.id, relationship_type=RelationshipType.BELONGS_TO)
    # Init -> Decision
    r4 = EntityRelationship(source_entity_id=init.id, target_entity_id=dec.id, relationship_type=RelationshipType.CONTAINS)
    # Decision -> PRD
    r5 = EntityRelationship(source_entity_id=dec.id, target_entity_id=prd.id, relationship_type=RelationshipType.IMPLEMENTS)
    # PRD -> KPI
    r6 = EntityRelationship(source_entity_id=prd.id, target_entity_id=kpi.id, relationship_type=RelationshipType.MEASURED_BY)

    test_session.add_all([r1, r2, r3, r4, r5, r6])
    await test_session.commit()

    engine = GraphTraversalEngine(db=test_session, workspace_id=ws_id)

    # 3. Test lineage tracing on Vendor Wallet
    lineage = await engine.trace_lineage(entity_id=init.id, max_depth=5)
    assert lineage is not None
    assert lineage.root_entity.name == "Vendor Wallet"

    # Verify upstream causes exist
    upstream_names = {u.name for u in lineage.upstream_nodes}
    assert "Automated Batch Wallet Settlements" in upstream_names
    assert "Vendor Payment Reconciliation Delays" in upstream_names

    # Verify downstream outcomes exist
    downstream_names = {d.name for d in lineage.downstream_nodes}
    assert "Approve Vendor Wallet MVP" in downstream_names
    assert "PRD: Vendor Wallet v1" in downstream_names
    assert "Reconciliation Time Reduced to < 2h" in downstream_names


@pytest.mark.asyncio
async def test_shortest_path(test_session):
    ws_id = TEST_WORKSPACE_ID
    e1 = Entity(id="n1", workspace_id=ws_id, entity_type=EntityType.PROBLEM, name="Slow Logistics")
    e2 = Entity(id="n2", workspace_id=ws_id, entity_type=EntityType.REQUIREMENT, name="Fast Dispatch")
    e3 = Entity(id="n3", workspace_id=ws_id, entity_type=EntityType.KPI, name="Dispatch SLA < 5m")

    test_session.add_all([e1, e2, e3])
    await test_session.flush()

    r1 = EntityRelationship(source_entity_id=e1.id, target_entity_id=e2.id, relationship_type=RelationshipType.SUPPORTS)
    r2 = EntityRelationship(source_entity_id=e2.id, target_entity_id=e3.id, relationship_type=RelationshipType.MEASURED_BY)
    test_session.add_all([r1, r2])
    await test_session.commit()

    engine = GraphTraversalEngine(db=test_session, workspace_id=ws_id)
    path = await engine.find_shortest_path(source_id="n1", target_id="n3")

    assert path.path_found is True
    assert path.distance == 2
    assert [n.id for n in path.nodes] == ["n1", "n2", "n3"]


@pytest.mark.asyncio
async def test_workspace_isolation(test_session):
    """
    Verifies zero cross-workspace data leakage:
    Entities belonging to Workspace B must NEVER be returned to Workspace A.
    """
    ws_a = TEST_WORKSPACE_ID
    ws_b = "ws-competitor-999"

    e_a = Entity(id="ent-a", workspace_id=ws_a, entity_type=EntityType.INITIATIVE, name="Alpha Project")
    e_b = Entity(id="ent-b", workspace_id=ws_b, entity_type=EntityType.INITIATIVE, name="Secret Competitor Initiative")
    test_session.add_all([e_a, e_b])
    await test_session.commit()

    # Traversal in Workspace A looking for B
    engine = GraphTraversalEngine(db=test_session, workspace_id=ws_a)
    subgraph = await engine.get_subgraph(start_entity_id="ent-b")
    assert len(subgraph.nodes) == 0

    path = await engine.find_shortest_path(source_id="ent-a", target_id="ent-b")
    assert path.path_found is False
