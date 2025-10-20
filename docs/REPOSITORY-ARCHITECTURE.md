# Repository Architecture

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Status:** Active strategy

---

## Overview

This document explains the repository architecture strategy for the home lab infrastructure and development projects. As of 2025-10-17, we transitioned from a monolithic `dev-lab` repository to a focused, purpose-specific repository structure.

---

## The Problem: Monolithic Repository

**What happened:**
- `dev-lab` repository grew to include everything: blockchain research, bug bounty tools, templates, network infrastructure, microservices
- Total scope became too large for AI assistants to maintain context
- AI responses showed confusion about what belonged where
- Documentation became scattered across unrelated domains
- Single repository made it hard to share specific components

**Symptoms:**
- "dev-lab is getting too big" - Context overload
- AI assistants mixing concerns (blockchain + infrastructure + bug bounty)
- Difficulty finding relevant files
- Git history mixing unrelated changes

---

## The Solution: Focused Repositories

**Strategy:** Split monolithic repository into focused, single-purpose repositories.

**Core Principle:** Each repository should have a clear, singular purpose that can be described in one sentence.

---

## Repository Inventory

### Active Repositories

| Repository | Purpose | Contents | Status |
|------------|---------|----------|--------|
| **dev-network** | Guardian Pi + Beast infrastructure | Network configs, monitoring, Docker compose, Cloudflare Tunnel | ✅ Active (2025-10-17) |
| **dev-guardian** | Guardian Pi architecture & planning | Architecture docs, setup guides, design specs | ✅ Active (2025-10-19) |
| **dev-lab** | General development workspace | Blockchain research, templates, learning materials | ✅ Active (reduced scope) |
| **ydun-scraper** | Article extraction microservice | Python Flask service, trafilatura integration | ✅ Active (2025-10-17) |

### Planned Repositories

| Repository | Purpose | Planned Contents | Priority |
|------------|---------|------------------|----------|
| **cardano-nodes** | Cardano blockchain infrastructure | Node configs, Aiken contracts, off-chain code | High |
| **ergo-nodes** | Ergo blockchain infrastructure | Node configs, ErgoScript, Rosen Bridge | Medium |
| **midnight-nodes** | Midnight blockchain infrastructure | Node configs, Compact contracts, ZK proofs | Medium |
| **mundus-context-engine** | Mundus personal context engine | Supabase integration, RAG system, UI | High |
| **security-tools** | Defensive security toolkit | Detection rules, analysis tools, documentation | Low |

---

## Decision Matrix: What Goes Where?

### dev-network

**Scope:** Physical and virtual infrastructure for home lab network

**Includes:**
- Guardian Pi deployment configs (Docker Compose, actual configs)
- Beast server configuration (Docker, system setup)
- Network-wide configs (DNS, firewall, routing)
- Monitoring infrastructure (Prometheus, Grafana)
- Cloudflare Tunnel configuration
- Infrastructure deployment documentation

**Excludes:**
- Guardian architecture/planning (belongs in dev-guardian)
- Application code (belongs in app-specific repos)
- Blockchain nodes (belong in chain-specific repos)
- Development tools (belong in dev-lab)

**Test:** "Is this about the infrastructure deployment configs, not the design/planning?"

---

### dev-guardian

**Scope:** Guardian Pi architecture, planning, and setup documentation

**Includes:**
- Guardian 2.0 architecture documentation
- Setup procedures and guides
- Design specifications
- Status tracking
- Planning documents

**Excludes:**
- Actual deployment configs (belong in dev-network/guardian/)
- Running services (deployed on Guardian Pi hardware)

**Test:** "Is this Guardian architecture/planning, not actual deployment configs?"

---

### dev-lab

**Scope:** General development workspace and learning environment

**Includes:**
- Project templates (AGENTS.md, CLAUDE.md, etc.)
- Blockchain research and documentation
- Learning materials and knowledge base
- Experimental code
- Documentation standards
- Cross-project utilities

**Excludes:**
- Production infrastructure (belongs in dev-network)
- Deployable services (belong in service-specific repos)
- Production blockchain nodes (belong in chain-specific repos)

**Test:** "Is this research, learning, or cross-project tooling?"

---

### ydun-scraper

**Scope:** Article extraction microservice for Mundus

**Includes:**
- Python Flask HTTP server
- Article extraction logic (trafilatura, newspaper3k)
- API endpoints
- Docker configuration
- Service-specific documentation

**Excludes:**
- Infrastructure deployment (belongs in dev-network)
- Mundus integration logic (belongs in mundus-context-engine)

**Test:** "Is this code that runs *inside* the scraper service?"

---

### Future: cardano-nodes

**Scope:** Cardano blockchain infrastructure

**Includes:**
- Node configuration and setup
- Aiken smart contracts
- Off-chain code (Lucid, Mesh)
- Cardano-specific documentation
- Testnet and mainnet configs

**Excludes:**
- General blockchain research (belongs in dev-lab)
- Infrastructure deployment (belongs in dev-network)

**Test:** "Is this Cardano-specific code or configuration?"

---

### Future: mundus-context-engine

**Scope:** Personal context engine and RAG system

**Includes:**
- Supabase schema and migrations
- Edge functions
- Frontend UI
- Article processing pipeline
- Integration with ydun-scraper
- Vector embeddings and search

**Excludes:**
- Scraper service code (belongs in ydun-scraper)
- Infrastructure deployment (belongs in dev-network)

**Test:** "Is this part of the Mundus application?"

---

## Benefits of Focused Repositories

### 1. AI Context Management
- AI assistants can load entire relevant repository
- No confusion about scope or purpose
- Better suggestions and code generation
- Clearer AGENTS.md files

### 2. Collaboration & Sharing
- Easy to share specific components
- Clear ownership boundaries
- Independent versioning
- Easier to open-source individual components

### 3. Development Workflow
- Faster git operations (smaller repos)
- Clearer commit history
- Easier to find relevant code
- Independent CI/CD pipelines

### 4. Documentation
- Focused, relevant documentation
- No cross-domain confusion
- Easier onboarding
- Clear README files

### 5. Deployment
- Independent deployment cycles
- Clear dependency boundaries
- Easier rollback procedures
- Service-specific monitoring

---

## Repository Standards

All repositories follow these standards:

### Required Files
- `AGENTS.md` - AI assistant guidelines and project context
- `CLAUDE.md` - Quick reference for Claude Code
- `JIMMYS-WORKFLOW.md` - RED/GREEN/CHECKPOINT methodology
- `README.md` - Project overview and quick start
- `.gitignore` - Appropriate for project type

### Documentation Standards
- Factual, objective language (no marketing speak)
- Include actual dates (ISO 8601: YYYY-MM-DD)
- Follow Jimmy's Workflow for implementations
- Document rollback procedures
- AI-readable structure (tables, clear headings)

### Git Standards
- Conventional commits format
- Include "🤖 Generated with Claude Code" footer
- Co-Authored-By: Claude <noreply@anthropic.com>
- Atomic commits (one logical change per commit)

---

## Migration Strategy

### Completed Migrations (2025-10-17)

**dev-network:**
- ✅ Created new repository
- ✅ Added project templates (AGENTS.md, CLAUDE.md, JIMMYS-WORKFLOW.md)
- ✅ Migrated Beast monitoring infrastructure
- ✅ Added Cloudflare Tunnel configuration
- ✅ Created comprehensive documentation
- ✅ Pushed to GitHub: https://github.com/Jimmyh-world/dev-network

**ydun-scraper:**
- ✅ Created new repository
- ✅ Added project templates
- ✅ Implemented Python Flask service
- ✅ Dockerized application
- ✅ Deployed on Beast
- ✅ Pushed to GitHub: https://github.com/Jimmyh-world/ydun-scraper

### Planned Migrations

**cardano-nodes** (Priority: High)
1. Create new repository
2. Migrate Cardano knowledge base from dev-lab/docs/cardano/
3. Set up node configuration
4. Document node operations
5. Deploy preview testnet node

**mundus-context-engine** (Priority: High)
1. Create new repository
2. Set up Supabase project structure
3. Implement edge functions
4. Create frontend UI
5. Integrate with ydun-scraper

---

## Cross-Repository Dependencies

### Current Dependencies

```
dev-network (infrastructure deployment)
  ├── Deploys: ydun-scraper (microservice)
  ├── References: dev-guardian (Guardian architecture/planning)
  └── References: dev-lab (templates)

dev-guardian (Guardian planning)
  └── Referenced by: dev-network (for deployment specs)

ydun-scraper (microservice)
  └── Called by: mundus-context-engine (planned)

dev-lab (workspace)
  └── Provides templates to: all repositories
```

### Dependency Management

**Templates:**
- Source of truth: `dev-lab/templates/`
- Projects copy templates during setup
- Projects may customize templates
- Sync templates manually when needed

**Infrastructure:**
- Deployment configs in `dev-network`
- Service code in service-specific repos
- Reference service repos via GitHub URLs
- Use Docker image tags for versioning

**Services:**
- Communicate via HTTP APIs
- Document API contracts in each repo
- Version APIs appropriately
- Use Cloudflare Tunnel for external access

---

## GitHub Organization

**Current Organization:** Personal GitHub account (Jimmyh-world)

### Repository URLs

- https://github.com/Jimmyh-world/dev-network
- https://github.com/Jimmyh-world/dev-guardian
- https://github.com/Jimmyh-world/dev-lab
- https://github.com/Jimmyh-world/ydun-scraper

### Visibility

All repositories currently **private**.

**Future consideration:** Open-source specific components:
- Project templates
- Documentation standards
- Reusable infrastructure patterns

---

## Local Development Structure

### Chromebook (`/home/jimmyb/`)

```
/home/jimmyb/
├── dev-lab/                    # General development workspace
│   ├── templates/              # Project templates (source of truth)
│   ├── docs/                   # Cross-project documentation
│   └── [various research]
│
├── dev-network/                # Infrastructure deployment configs
│   ├── beast/                  # Beast server configs
│   ├── guardian/               # Guardian Pi deployment configs
│   └── docs/                   # Infrastructure documentation
│
├── dev-guardian/               # Guardian Pi architecture & planning
│   ├── docs/                   # Architecture, setup guides
│   ├── STATUS.md               # Guardian project status
│   └── NEXT-SESSION-START-HERE.md
│
├── ydun-scraper/               # Article extraction service
│   ├── src/                    # Service source code
│   ├── Dockerfile              # Container definition
│   └── README.md
│
└── [future repos]/             # Additional focused repositories
```

### Beast (`/home/jimmyb/`)

```
/home/jimmyb/
├── dev-network/     # Infrastructure configs (pulled from GitHub)
│   ├── beast/docker/          # Docker compose configs
│   ├── beast/monitoring/      # Prometheus, Grafana configs
│   └── beast/cloudflare/      # Tunnel configs
│
└── ydun-scraper/              # Scraper service (pulled from GitHub)
    └── [built and running in Docker]
```

---

## Naming Conventions

### Repository Names
- Lowercase with hyphens: `dev-network`
- Descriptive, not abbreviated: `ydun-scraper` not `ys`
- Singular for services: `mundus-context-engine`
- Plural for collections: `cardano-nodes`

### Branch Names
- `main` - Primary branch (not `master`)
- `feature/description` - Feature branches
- `fix/description` - Bug fix branches
- `docs/description` - Documentation updates

### File Naming
- Uppercase for important docs: `README.md`, `AGENTS.md`
- Lowercase for code: `http_server.py`, `config.yml`
- Hyphens for multi-word: `docker-compose.yml`
- Descriptive names: `NEXT-SESSION-START-HERE.md`

---

## Future Considerations

### Monorepo vs Polyrepo

**Current choice:** Polyrepo (multiple focused repositories)

**Rationale:**
- Better for AI context management
- Clearer boundaries
- Independent deployment
- Easier to understand scope

**Future:** If cross-repo changes become frequent, consider monorepo tools (Nx, Turborepo)

### Repository Templates

**Planned:** GitHub repository template for new projects

**Would include:**
- Pre-configured AGENTS.md, CLAUDE.md, JIMMYS-WORKFLOW.md
- Standard .gitignore patterns
- README.md template
- GitHub Actions workflows (optional)

### Automation

**Planned automation:**
- Template sync script (dev-lab/templates → other repos)
- Repository health checks (missing files, outdated templates)
- Cross-repo documentation links validation

---

## Lessons Learned

### What Worked

1. **Early split:** Splitting before repositories got too large
2. **Clear purpose:** Each repo has single, clear purpose
3. **Template standards:** Consistent structure across repos
4. **Documentation first:** Document architecture before migrating

### What to Avoid

1. **Too granular:** Don't create repo for every tiny service
2. **Unclear boundaries:** Define what goes where upfront
3. **Duplicate docs:** Keep single source of truth
4. **Inconsistent standards:** Maintain template compliance

### Best Practices

1. **Ask the question:** "Can I describe this repo's purpose in one sentence?"
2. **Test the boundary:** Use decision matrix to validate placement
3. **Document decisions:** Record why things are where they are
4. **Regular review:** Reassess architecture as projects grow

---

## Questions & Answers

**Q: What if code needs to be shared between repos?**
A: Extract to library, publish as package, or duplicate if small. Document the decision.

**Q: How do we keep templates in sync?**
A: Manual sync when needed. Templates evolve slowly, so this is acceptable.

**Q: What about secrets and credentials?**
A: Always gitignored. Document *where* they're stored, not the secrets themselves.

**Q: Should infrastructure code live with application code?**
A: No. Infrastructure deployment lives in dev-network. Application code lives in app repo.

**Q: When should we create a new repository?**
A: When a component has a clear, singular purpose and benefits from independent lifecycle.

---

## Conclusion

The focused repository architecture provides:
- Clear boundaries and ownership
- Better AI assistant performance
- Easier collaboration and sharing
- Independent deployment cycles
- Clearer documentation

This strategy supports the long-term maintainability and growth of the home lab infrastructure.

---

**This architecture is a living document. Update as we learn and evolve.**

---

**Last Updated:** 2025-10-17
