# Roadmap

Future improvements and long-term vision for the project.

## Phase 5: Web Interface

**Timeframe**: 1-2 weeks  
**Impact**: High usability  
**Difficulty**: Medium

- [ ] Build web UI (Flask/FastAPI + React/Vue)
- [ ] REST API endpoints
- [ ] Real-time scan progress via WebSocket
- [ ] Dashboard with scan history
- [ ] Deploy to Heroku/Railway

**Why**: Current GUI limited to local machine; web UI enables remote scanning.

---

## Phase 6: Database Backend

**Timeframe**: 1-2 weeks  
**Impact**: Medium  
**Difficulty**: Medium

- [ ] SQLite/PostgreSQL integration
- [ ] Scan history persistence
- [ ] Malware signature database
- [ ] User management (multi-user)
- [ ] API authentication

**Why**: JSON files don't scale; database enables features like scan history, collaboration.

---

## Phase 7: YARA Rules Integration

**Timeframe**: 1-2 weeks  
**Impact**: Medium  
**Difficulty**: Hard

- [ ] YARA rule support (in addition to hashes)
- [ ] Pattern-based detection (strings, bytes, regex)
- [ ] Community rule repository integration
- [ ] Rule validation & testing

**Why**: YARA is industry standard; teaches pattern matching beyond hashing.

---

## Phase 8: Machine Learning Detection

**Timeframe**: 1-2 months  
**Impact**: High  
**Difficulty**: Hard

- [ ] Static analysis features (PE headers, imports, entropy)
- [ ] ML classifier (sklearn Random Forest/XGBoost)
- [ ] Train on benign vs malware samples
- [ ] Heuristic scoring system
- [ ] Feature importance visualization

**Why**: Teach ML in security context; detect unknown threats.

**Warning**: Educational implementation, not production-grade.

---

## Phase 9: Real-Time Monitoring

**Timeframe**: 1-2 months  
**Impact**: High  
**Difficulty**: Hard

- [ ] File system watcher (watchdog library)
- [ ] Real-time scan on file creation/modification
- [ ] Live alerts and notifications
- [ ] Performance optimization (threading/async)

**Why**: Learn async I/O; demonstrate real-time systems.

---

## Phase 10: REST API Server

**Timeframe**: 1 month  
**Impact**: High  
**Difficulty**: Medium

- [ ] FastAPI application
- [ ] Scan endpoint (`POST /scan`)
- [ ] Reports endpoint (`GET /reports/{id}`)
- [ ] Signature management endpoints
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Rate limiting & authentication

**Why**: Integration point for third-party tools; demonstrate API design.

---

## Phase 11: Advanced Reporting

**Timeframe**: 2-3 weeks  
**Impact**: Medium  
**Difficulty**: Medium

- [ ] PDF reports (reportlab)
- [ ] Email alerts (SMTP)
- [ ] Custom report templates
- [ ] Data visualization (charts, graphs)
- [ ] Export to multiple formats (XLSX, CSV)

**Why**: Teach reporting patterns; improve user experience.

---

## Phase 12: Automatic Updates

**Timeframe**: 1 week  
**Impact**: Medium  
**Difficulty**: Easy

- [ ] Background signature updates
- [ ] Check for new threat feeds daily
- [ ] Automatic version upgrades
- [ ] Changelog notifications

**Why**: Production systems need automated updates; demonstrate DevOps concepts.

---

## Long-Term Vision (6+ months)

### Distributed Scanning
- Multiple workers scanning in parallel
- Job queue (Celery/RQ)
- Load balancing

### Threat Intelligence Feeds
- Integrate multiple sources (VirusTotal, YARA Community, AlienVault)
- Merge & deduplicate signatures
- Reputation scoring

### Kubernetes Deployment
- Docker containerization
- Helm charts
- Multi-instance scaling

### Advanced Machine Learning
- Deep learning models (CNN for binary analysis)
- Transfer learning from large datasets
- Adversarial robustness testing

### Browser Extension
- Scan downloads automatically
- Warn on suspicious files
- Integration with web-based UI

### Cross-Platform Agent
- Windows service/daemon
- macOS LaunchAgent
- Linux systemd service
- Central management console

---

## Contribution Ideas by Difficulty

### Easy (Good First Issues)

- [ ] Add more unit tests (aim for 100% coverage)
- [ ] Improve error messages and validation
- [ ] Add configuration examples and templates
- [ ] Create video tutorials
- [ ] Translate documentation
- [ ] Performance benchmarking tests
- [ ] Add more exclusion patterns examples

### Medium

- [ ] Web UI (Flask/FastAPI + HTML/CSS/JS)
- [ ] Database persistence (SQLite)
- [ ] Additional GUI layouts (PyQt, wxPython)
- [ ] Custom report templates
- [ ] Benchmark/performance tests
- [ ] Educational labs with sample files
- [ ] Docker container configuration

### Hard

- [ ] ML detection module with scikit-learn
- [ ] Real-time monitoring with watchdog
- [ ] REST API server (FastAPI)
- [ ] YARA rule integration
- [ ] Async/await refactoring for performance
- [ ] Advanced threat feeds integration

---

## Decision Criteria

When proposing new features, consider:

✅ **Educational value**: Teaches important security/Python concepts  
✅ **Scope**: Can be completed in reasonable time  
✅ **Maintainability**: Won't add technical debt  
✅ **Dependencies**: Minimal external dependencies  

❌ **Production features**: Not needed for educational project  
❌ **Heuristics beyond scope**: Save for advanced modules  
❌ **Heavy frameworks**: Prefer simplicity  
❌ **Vendor lock-in**: Stay platform-independent  

---

## How to Propose a Feature

1. Open a GitHub issue with:
   - **Title**: Brief feature name
   - **Learning objective**: What does this teach?
   - **Implementation sketch**: How would you build it?
   - **Timeline**: How long would it take?
   - **Dependencies**: What would you need?

2. Wait for maintainer feedback
3. Once approved, fork and create PR with:
   - Unit tests (80%+ coverage)
   - Documentation updates
   - Examples

---

## Success Metrics

We measure success by:

📈 **Learning impact**: Do students understand the concept?  
📈 **Code quality**: Is it maintainable and clear?  
📈 **Community**: Do contributors engage?  
📈 **Adoption**: Are people using it?  

Not by: production metrics, performance benchmarks, enterprise features.

---

**Have an idea?** Open an issue on [GitHub](https://github.com/Nekas1980/anti-virus-projeto/issues) 🚀
