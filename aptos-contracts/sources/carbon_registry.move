/// Enhanced Carbon Registry with CRUD operations and event emission
/// Fully deployable on Aptos testnet with frontend/backend integration
module carbon_registry::registry {
    use std::string::{Self, String};
    use std::signer;
    use aptos_framework::timestamp;
    use aptos_framework::account;
    use aptos_framework::event::{Self, EventHandle};
    use aptos_std::table::{Self, Table};

    /// Error codes
    const E_NOT_INITIALIZED: u64 = 1;
    const E_ALREADY_INITIALIZED: u64 = 2;
    const E_NOT_AUTHORIZED: u64 = 3;
    const E_PROJECT_NOT_FOUND: u64 = 4;
    const E_PROJECT_ALREADY_EXISTS: u64 = 5;
    const E_INVALID_AMOUNT: u64 = 6;
    const E_INSUFFICIENT_CREDITS: u64 = 7;

    /// Project structure with full CRUD support
    struct Project has store, copy, drop {
        id: String,
        owner: address,
        name: String,
        location: String,
        area: u64,              // hectares * 100
        carbon_credits: u64,    // tons * 100
        status: u8,             // 0=draft, 1=active, 2=verified, 3=retired
        created_at: u64,
        updated_at: u64,
    }

    /// Global registry storage
    struct Registry has key {
        projects: Table<String, Project>,
        project_count: u64,
        total_credits: u64,
        admin: address,
    }

    /// Event structures for frontend/backend listening
    struct ProjectCreatedEvent has drop, store {
        project_id: String,
        owner: address,
        name: String,
        carbon_credits: u64,
        timestamp: u64,
    }

    struct ProjectUpdatedEvent has drop, store {
        project_id: String,
        owner: address,
        field_updated: String,
        timestamp: u64,
    }

    struct ProjectDeletedEvent has drop, store {
        project_id: String,
        owner: address,
        timestamp: u64,
    }

    struct CreditsTransferredEvent has drop, store {
        project_id: String,
        from: address,
        to: address,
        amount: u64,
        timestamp: u64,
    }

    /// Event handles
    struct EventHandles has key {
        project_created_events: EventHandle<ProjectCreatedEvent>,
        project_updated_events: EventHandle<ProjectUpdatedEvent>,
        project_deleted_events: EventHandle<ProjectDeletedEvent>,
        credits_transferred_events: EventHandle<CreditsTransferredEvent>,
    }

    /// Initialize the registry (call once)
    public entry fun initialize(admin: &signer) {
        let admin_addr = signer::address_of(admin);
        
        // Ensure not already initialized
        assert!(!exists<Registry>(admin_addr), E_ALREADY_INITIALIZED);
        
        // Create registry
        move_to(admin, Registry {
            projects: table::new(),
            project_count: 0,
            total_credits: 0,
            admin: admin_addr,
        });

        // Create event handles
        move_to(admin, EventHandles {
            project_created_events: account::new_event_handle<ProjectCreatedEvent>(admin),
            project_updated_events: account::new_event_handle<ProjectUpdatedEvent>(admin),
            project_deleted_events: account::new_event_handle<ProjectDeletedEvent>(admin),
            credits_transferred_events: account::new_event_handle<CreditsTransferredEvent>(admin),
        });
    }

    /// CREATE: Add new project
    public entry fun create_project(
        owner: &signer,
        registry_addr: address,
        project_id: String,
        name: String,
        location: String,
        area: u64,
        carbon_credits: u64,
    ) acquires Registry, EventHandles {
        let owner_addr = signer::address_of(owner);
        
        // Get registry
        assert!(exists<Registry>(registry_addr), E_NOT_INITIALIZED);
        let registry = borrow_global_mut<Registry>(registry_addr);
        
        // Check project doesn't exist
        assert!(!table::contains(&registry.projects, project_id), E_PROJECT_ALREADY_EXISTS);
        assert!(carbon_credits > 0, E_INVALID_AMOUNT);

        let now = timestamp::now_seconds();

        // Create project
        let project = Project {
            id: project_id,
            owner: owner_addr,
            name,
            location,
            area,
            carbon_credits,
            status: 1, // active
            created_at: now,
            updated_at: now,
        };

        // Add to registry
        table::add(&mut registry.projects, project_id, project);
        registry.project_count = registry.project_count + 1;
        registry.total_credits = registry.total_credits + carbon_credits;

        // Emit event
        let event_handles = borrow_global_mut<EventHandles>(registry_addr);
        event::emit_event(&mut event_handles.project_created_events, ProjectCreatedEvent {
            project_id,
            owner: owner_addr,
            name,
            carbon_credits,
            timestamp: now,
        });
    }

    /// READ: Get project details (view function)
    #[view]
    public fun get_project(registry_addr: address, project_id: String): Project acquires Registry {
        assert!(exists<Registry>(registry_addr), E_NOT_INITIALIZED);
        let registry = borrow_global<Registry>(registry_addr);
        assert!(table::contains(&registry.projects, project_id), E_PROJECT_NOT_FOUND);
        *table::borrow(&registry.projects, project_id)
    }

    /// READ: Get all project IDs (for listing)
    #[view]
    public fun get_project_count(registry_addr: address): u64 acquires Registry {
        assert!(exists<Registry>(registry_addr), E_NOT_INITIALIZED);
        let registry = borrow_global<Registry>(registry_addr);
        registry.project_count
    }

    /// READ: Get total credits
    #[view]
    public fun get_total_credits(registry_addr: address): u64 acquires Registry {
        assert!(exists<Registry>(registry_addr), E_NOT_INITIALIZED);
        let registry = borrow_global<Registry>(registry_addr);
        registry.total_credits
    }

    /// UPDATE: Update project name
    public entry fun update_project_name(
        owner: &signer,
        registry_addr: address,
        project_id: String,
        new_name: String,
    ) acquires Registry, EventHandles {
        let owner_addr = signer::address_of(owner);
        
        assert!(exists<Registry>(registry_addr), E_NOT_INITIALIZED);
        let registry = borrow_global_mut<Registry>(registry_addr);
        
        assert!(table::contains(&registry.projects, project_id), E_PROJECT_NOT_FOUND);
        let project = table::borrow_mut(&mut registry.projects, project_id);
        
        // Check ownership
        assert!(project.owner == owner_addr, E_NOT_AUTHORIZED);
        
        // Update
        project.name = new_name;
        project.updated_at = timestamp::now_seconds();

        // Emit event
        let event_handles = borrow_global_mut<EventHandles>(registry_addr);
        event::emit_event(&mut event_handles.project_updated_events, ProjectUpdatedEvent {
            project_id,
            owner: owner_addr,
            field_updated: string::utf8(b"name"),
            timestamp: timestamp::now_seconds(),
        });
    }

    /// UPDATE: Update project location
    public entry fun update_project_location(
        owner: &signer,
        registry_addr: address,
        project_id: String,
        new_location: String,
    ) acquires Registry, EventHandles {
        let owner_addr = signer::address_of(owner);
        
        assert!(exists<Registry>(registry_addr), E_NOT_INITIALIZED);
        let registry = borrow_global_mut<Registry>(registry_addr);
        
        assert!(table::contains(&registry.projects, project_id), E_PROJECT_NOT_FOUND);
        let project = table::borrow_mut(&mut registry.projects, project_id);
        
        assert!(project.owner == owner_addr, E_NOT_AUTHORIZED);
        
        project.location = new_location;
        project.updated_at = timestamp::now_seconds();

        let event_handles = borrow_global_mut<EventHandles>(registry_addr);
        event::emit_event(&mut event_handles.project_updated_events, ProjectUpdatedEvent {
            project_id,
            owner: owner_addr,
            field_updated: string::utf8(b"location"),
            timestamp: timestamp::now_seconds(),
        });
    }

    /// UPDATE: Update project status
    public entry fun update_project_status(
        owner: &signer,
        registry_addr: address,
        project_id: String,
        new_status: u8,
    ) acquires Registry, EventHandles {
        let owner_addr = signer::address_of(owner);
        
        assert!(exists<Registry>(registry_addr), E_NOT_INITIALIZED);
        let registry = borrow_global_mut<Registry>(registry_addr);
        
        assert!(table::contains(&registry.projects, project_id), E_PROJECT_NOT_FOUND);
        let project = table::borrow_mut(&mut registry.projects, project_id);
        
        assert!(project.owner == owner_addr, E_NOT_AUTHORIZED);
        
        project.status = new_status;
        project.updated_at = timestamp::now_seconds();

        let event_handles = borrow_global_mut<EventHandles>(registry_addr);
        event::emit_event(&mut event_handles.project_updated_events, ProjectUpdatedEvent {
            project_id,
            owner: owner_addr,
            field_updated: string::utf8(b"status"),
            timestamp: timestamp::now_seconds(),
        });
    }

    /// DELETE: Remove project (soft delete by setting status to retired)
    public entry fun delete_project(
        owner: &signer,
        registry_addr: address,
        project_id: String,
    ) acquires Registry, EventHandles {
        let owner_addr = signer::address_of(owner);
        
        assert!(exists<Registry>(registry_addr), E_NOT_INITIALIZED);
        let registry = borrow_global_mut<Registry>(registry_addr);
        
        assert!(table::contains(&registry.projects, project_id), E_PROJECT_NOT_FOUND);
        let project = table::borrow_mut(&mut registry.projects, project_id);
        
        assert!(project.owner == owner_addr, E_NOT_AUTHORIZED);
        
        // Soft delete - set status to retired
        project.status = 3;
        project.updated_at = timestamp::now_seconds();

        // Emit event
        let event_handles = borrow_global_mut<EventHandles>(registry_addr);
        event::emit_event(&mut event_handles.project_deleted_events, ProjectDeletedEvent {
            project_id,
            owner: owner_addr,
            timestamp: timestamp::now_seconds(),
        });
    }

    /// Transfer credits between projects
    public entry fun transfer_credits(
        owner: &signer,
        registry_addr: address,
        from_project_id: String,
        to_project_id: String,
        amount: u64,
    ) acquires Registry, EventHandles {
        let owner_addr = signer::address_of(owner);
        
        assert!(exists<Registry>(registry_addr), E_NOT_INITIALIZED);
        let registry = borrow_global_mut<Registry>(registry_addr);
        
        // Check both projects exist
        assert!(table::contains(&registry.projects, from_project_id), E_PROJECT_NOT_FOUND);
        assert!(table::contains(&registry.projects, to_project_id), E_PROJECT_NOT_FOUND);
        
        // Get from project
        let from_project = table::borrow_mut(&mut registry.projects, from_project_id);
        assert!(from_project.owner == owner_addr, E_NOT_AUTHORIZED);
        assert!(from_project.carbon_credits >= amount, E_INSUFFICIENT_CREDITS);
        
        // Deduct from source
        from_project.carbon_credits = from_project.carbon_credits - amount;
        from_project.updated_at = timestamp::now_seconds();
        
        // Add to destination
        let to_project = table::borrow_mut(&mut registry.projects, to_project_id);
        to_project.carbon_credits = to_project.carbon_credits + amount;
        to_project.updated_at = timestamp::now_seconds();

        // Emit event
        let event_handles = borrow_global_mut<EventHandles>(registry_addr);
        event::emit_event(&mut event_handles.credits_transferred_events, CreditsTransferredEvent {
            project_id: from_project_id,
            from: owner_addr,
            to: to_project.owner,
            amount,
            timestamp: timestamp::now_seconds(),
        });
    }

    /// Check if project exists
    #[view]
    public fun project_exists(registry_addr: address, project_id: String): bool acquires Registry {
        if (!exists<Registry>(registry_addr)) {
            return false
        };
        let registry = borrow_global<Registry>(registry_addr);
        table::contains(&registry.projects, project_id)
    }

    /// Get registry info
    #[view]
    public fun get_registry_info(registry_addr: address): (u64, u64, address) acquires Registry {
        assert!(exists<Registry>(registry_addr), E_NOT_INITIALIZED);
        let registry = borrow_global<Registry>(registry_addr);
        (registry.project_count, registry.total_credits, registry.admin)
    }
}
