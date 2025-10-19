## Monitoring Migration

**Status:** Planned - To Be Executed
**Spec:** See `~/dev-guardian/docs/MONITORING-MIGRATION-SPEC.md`

**Decision:** Move Prometheus + Grafana from Beast to Guardian

**Reason:** 
- Guardian's role = always watching (monitoring should be on Guardian)
- Guardian never sleeps (monitoring always available)
- Beast can sleep while monitored
- Aligns with Guardian 2.0 architecture

**Execution Plan:** See spec in dev-guardian repository

**Timeline:** 2-3 hours + 2 days validation

**Cross-Reference:** 
- Design: `~/dev-guardian/docs/MONITORING-MIGRATION-SPEC.md`
- Beast configs: `~/dev-network/beast/docker/docker-compose.yml`

