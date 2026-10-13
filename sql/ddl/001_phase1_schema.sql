-- Phase 1 physical tables are created from validated pandas relations because
-- measurements_wide has source-dependent dynamic columns. This file documents
-- the stable relational contract enforced by src/yieldguard/pipeline.py.

-- fact_production_entity grain: one row per entity_id (unique index enforced).
-- measurements_wide grain: one row per entity_id (unique index enforced).
-- dim_sensor grain: one row per sensor_id (unique index enforced).
-- audit_split_candidate grain: one row per configured candidate allocation.

-- The rebuildable database lives at data/processed/yieldguard.duckdb and is not
-- committed. Use `yieldguard build-phase1` to recreate it from validated source.
