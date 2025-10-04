/// Carbon Credit Registry Smart Contract
/// Manages carbon credits, GeoNFTs, and tokenization on Aptos blockchain
module carbon_registry::carbon_credit {
    use std::string::{Self, String};
    use std::signer;
    use std::vector;
    use aptos_framework::timestamp;
    use aptos_framework::coin;
    use aptos_framework::account;
    use aptos_framework::event::{Self, EventHandle};
    use aptos_std::table::{Self, Table};

    /// Error codes
    const E_NOT_AUTHORIZED: u64 = 1;
    const E_PROJECT_NOT_FOUND: u64 = 2;
    const E_INSUFFICIENT_CREDITS: u64 = 3;
    const E_ALREADY_INITIALIZED: u64 = 4;
    const E_INVALID_AMOUNT: u64 = 5;
    const E_PROJECT_ALREADY_EXISTS: u64 = 6;

    /// Carbon Credit Project structure
    struct CarbonProject has key, store, copy, drop {
        project_id: String,
        owner: address,
        location: String,
        latitude: u64,  // Stored as integer (multiply by 1000000)
        longitude: u64, // Stored as integer (multiply by 1000000)
        area: u64,      // In hectares * 100
        total_credits: u64,  // Total carbon credits * 100
        available_credits: u64,
        retired_credits: u64,
        unit_price: u64,  // Price in APT * 100
        vintage_year: u64,
        verification_status: u8,  // 0=pending, 1=verified, 2=rejected
        created_at: u64,
        geonft_id: String,
    }

    /// GeoNFT structure - Location-bound NFT
    struct GeoNFT has key, store, copy, drop {
        nft_id: String,
        project_id: String,
        owner: address,
        latitude: u64,
        longitude: u64,
        metadata_uri: String,
        is_location_verified: bool,
        created_at: u64,
    }

    /// Carbon Credit Token
    struct CarbonToken has key, store, copy, drop {
        token_id: String,
        project_id: String,
        amount: u64,
        owner: address,
        is_retired: bool,
    }

    /// Registry to store all projects
    struct ProjectRegistry has key {
        projects: Table<String, CarbonProject>,
        project_count: u64,
        total_credits_issued: u64,
        total_credits_retired: u64,
    }

    /// GeoNFT Registry
    struct GeoNFTRegistry has key {
        nfts: Table<String, GeoNFT>,
        nft_count: u64,
    }

    /// Events
    struct ProjectCreatedEvent has drop, store {
        project_id: String,
        owner: address,
        total_credits: u64,
        timestamp: u64,
    }

    struct CreditsTransferredEvent has drop, store {
        project_id: String,
        from: address,
        to: address,
        amount: u64,
        timestamp: u64,
    }

    struct CreditsRetiredEvent has drop, store {
        project_id: String,
        owner: address,
        amount: u64,
        timestamp: u64,
    }

    struct GeoNFTMintedEvent has drop, store {
        nft_id: String,
        project_id: String,
        owner: address,
        timestamp: u64,
    }

    /// Event handles
    struct EventHandles has key {
        project_created_events: EventHandle<ProjectCreatedEvent>,
        credits_transferred_events: EventHandle<CreditsTransferredEvent>,
        credits_retired_events: EventHandle<CreditsRetiredEvent>,
        geonft_minted_events: EventHandle<GeoNFTMintedEvent>,
    }

    /// Initialize the module
    public entry fun initialize(account: &signer) {
        let account_addr = signer::address_of(account);
        
        assert!(!exists<ProjectRegistry>(account_addr), E_ALREADY_INITIALIZED);
        
        move_to(account, ProjectRegistry {
            projects: table::new(),
            project_count: 0,
            total_credits_issued: 0,
            total_credits_retired: 0,
        });

        move_to(account, GeoNFTRegistry {
            nfts: table::new(),
            nft_count: 0,
        });

        move_to(account, EventHandles {
            project_created_events: account::new_event_handle<ProjectCreatedEvent>(account),
            credits_transferred_events: account::new_event_handle<CreditsTransferredEvent>(account),
            credits_retired_events: account::new_event_handle<CreditsRetiredEvent>(account),
            geonft_minted_events: account::new_event_handle<GeoNFTMintedEvent>(account),
        });
    }

    /// Create a new carbon credit project
    public entry fun create_project(
        account: &signer,
        registry_addr: address,
        project_id: String,
        location: String,
        latitude: u64,
        longitude: u64,
        area: u64,
        total_credits: u64,
        unit_price: u64,
        vintage_year: u64,
    ) acquires ProjectRegistry, EventHandles {
        let owner = signer::address_of(account);
        let registry = borrow_global_mut<ProjectRegistry>(registry_addr);
        
        assert!(!table::contains(&registry.projects, project_id), E_PROJECT_ALREADY_EXISTS);
        assert!(total_credits > 0, E_INVALID_AMOUNT);

        let project = CarbonProject {
            project_id,
            owner,
            location,
            latitude,
            longitude,
            area,
            total_credits,
            available_credits: total_credits,
            retired_credits: 0,
            unit_price,
            vintage_year,
            verification_status: 0,
            created_at: timestamp::now_seconds(),
            geonft_id: string::utf8(b""),
        };

        table::add(&mut registry.projects, project_id, project);
        registry.project_count = registry.project_count + 1;
        registry.total_credits_issued = registry.total_credits_issued + total_credits;

        // Emit event
        let event_handles = borrow_global_mut<EventHandles>(registry_addr);
        event::emit_event(&mut event_handles.project_created_events, ProjectCreatedEvent {
            project_id,
            owner,
            total_credits,
            timestamp: timestamp::now_seconds(),
        });
    }

    /// Mint GeoNFT for a project
    public entry fun mint_geonft(
        account: &signer,
        registry_addr: address,
        nft_id: String,
        project_id: String,
        metadata_uri: String,
    ) acquires ProjectRegistry, GeoNFTRegistry, EventHandles {
        let owner = signer::address_of(account);
        let project_registry = borrow_global_mut<ProjectRegistry>(registry_addr);
        
        assert!(table::contains(&project_registry.projects, project_id), E_PROJECT_NOT_FOUND);
        
        let project = table::borrow_mut(&mut project_registry.projects, project_id);
        assert!(project.owner == owner, E_NOT_AUTHORIZED);

        let geonft_registry = borrow_global_mut<GeoNFTRegistry>(registry_addr);

        let geonft = GeoNFT {
            nft_id,
            project_id,
            owner,
            latitude: project.latitude,
            longitude: project.longitude,
            metadata_uri,
            is_location_verified: true,
            created_at: timestamp::now_seconds(),
        };

        table::add(&mut geonft_registry.nfts, nft_id, geonft);
        geonft_registry.nft_count = geonft_registry.nft_count + 1;
        
        // Update project with GeoNFT ID
        project.geonft_id = nft_id;

        // Emit event
        let event_handles = borrow_global_mut<EventHandles>(registry_addr);
        event::emit_event(&mut event_handles.geonft_minted_events, GeoNFTMintedEvent {
            nft_id,
            project_id,
            owner,
            timestamp: timestamp::now_seconds(),
        });
    }

    /// Transfer carbon credits
    public entry fun transfer_credits(
        account: &signer,
        registry_addr: address,
        project_id: String,
        to: address,
        amount: u64,
    ) acquires ProjectRegistry, EventHandles {
        let from = signer::address_of(account);
        let registry = borrow_global_mut<ProjectRegistry>(registry_addr);
        
        assert!(table::contains(&registry.projects, project_id), E_PROJECT_NOT_FOUND);
        
        let project = table::borrow_mut(&mut registry.projects, project_id);
        assert!(project.owner == from, E_NOT_AUTHORIZED);
        assert!(project.available_credits >= amount, E_INSUFFICIENT_CREDITS);

        project.available_credits = project.available_credits - amount;
        
        // In a full implementation, you would transfer ownership or create a token
        // For now, we just update the available credits

        // Emit event
        let event_handles = borrow_global_mut<EventHandles>(registry_addr);
        event::emit_event(&mut event_handles.credits_transferred_events, CreditsTransferredEvent {
            project_id,
            from,
            to,
            amount,
            timestamp: timestamp::now_seconds(),
        });
    }

    /// Retire carbon credits
    public entry fun retire_credits(
        account: &signer,
        registry_addr: address,
        project_id: String,
        amount: u64,
    ) acquires ProjectRegistry, EventHandles {
        let owner = signer::address_of(account);
        let registry = borrow_global_mut<ProjectRegistry>(registry_addr);
        
        assert!(table::contains(&registry.projects, project_id), E_PROJECT_NOT_FOUND);
        
        let project = table::borrow_mut(&mut registry.projects, project_id);
        assert!(project.owner == owner, E_NOT_AUTHORIZED);
        assert!(project.available_credits >= amount, E_INSUFFICIENT_CREDITS);

        project.available_credits = project.available_credits - amount;
        project.retired_credits = project.retired_credits + amount;
        registry.total_credits_retired = registry.total_credits_retired + amount;

        // Emit event
        let event_handles = borrow_global_mut<EventHandles>(registry_addr);
        event::emit_event(&mut event_handles.credits_retired_events, CreditsRetiredEvent {
            project_id,
            owner,
            amount,
            timestamp: timestamp::now_seconds(),
        });
    }

    /// Update verification status
    public entry fun update_verification_status(
        account: &signer,
        registry_addr: address,
        project_id: String,
        status: u8,
    ) acquires ProjectRegistry {
        let verifier = signer::address_of(account);
        let registry = borrow_global_mut<ProjectRegistry>(registry_addr);
        
        // In production, check if verifier is authorized
        assert!(table::contains(&registry.projects, project_id), E_PROJECT_NOT_FOUND);
        
        let project = table::borrow_mut(&mut registry.projects, project_id);
        project.verification_status = status;
    }

    /// View functions
    #[view]
    public fun get_project(registry_addr: address, project_id: String): CarbonProject acquires ProjectRegistry {
        let registry = borrow_global<ProjectRegistry>(registry_addr);
        *table::borrow(&registry.projects, project_id)
    }

    #[view]
    public fun get_geonft(registry_addr: address, nft_id: String): GeoNFT acquires GeoNFTRegistry {
        let registry = borrow_global<GeoNFTRegistry>(registry_addr);
        *table::borrow(&registry.nfts, nft_id)
    }

    #[view]
    public fun get_project_count(registry_addr: address): u64 acquires ProjectRegistry {
        let registry = borrow_global<ProjectRegistry>(registry_addr);
        registry.project_count
    }

    #[view]
    public fun get_total_credits_issued(registry_addr: address): u64 acquires ProjectRegistry {
        let registry = borrow_global<ProjectRegistry>(registry_addr);
        registry.total_credits_issued
    }

    #[view]
    public fun get_total_credits_retired(registry_addr: address): u64 acquires ProjectRegistry {
        let registry = borrow_global<ProjectRegistry>(registry_addr);
        registry.total_credits_retired
    }
}
