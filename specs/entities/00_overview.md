# Entity System Overview

## Core Components

### Entity Base
```c
typedef struct Entity {
    // Core properties
    uint32_t id;
    const char* name;
    bool active;
    bool visible;
    
    // Transform
    Vector2 position;
    float rotation;
    Vector2 scale;
    
    // Component system
    Component** components;
    int componentCount;
    int componentCapacity;
    
    // Hierarchy
    Entity* parent;
    Entity** children;
    int childCount;
    
    // Tags and layers
    uint32_t tags;
    uint32_t layer;
} Entity;
```

### Component System
```c
typedef struct Component {
    // Core properties
    ComponentType type;
    Entity* entity;
    bool enabled;
    
    // Lifecycle methods
    void (*Init)(Component* component);
    void (*Start)(Component* component);
    void (*Update)(Component* component);
    void (*LateUpdate)(Component* component);
    void (*OnDestroy)(Component* component);
    
    // Message system
    void (*OnMessage)(Component* component, const Message* message);
    void (*SendMessage)(Component* component, Message* message);
} Component;
```

## Entity Categories

### Game Objects
```c
typedef struct GameObject {
    Entity base;
    
    // Game object specific
    PhysicsBody* body;
    Sprite* sprite;
    Animator* animator;
    
    // Collision handling
    void (*OnCollision)(GameObject* self, GameObject* other);
    void (*OnTrigger)(GameObject* self, GameObject* other);
} GameObject;
```

### UI Elements
```c
typedef struct UIEntity {
    Entity base;
    
    // UI specific
    Rectangle bounds;
    Color color;
    bool interactive;
    
    // Event handlers
    void (*OnClick)(UIEntity* self);
    void (*OnHover)(UIEntity* self);
    void (*OnFocus)(UIEntity* self);
} UIEntity;
```

### Particle Systems
```c
typedef struct ParticleEntity {
    Entity base;
    
    // Emitter properties
    Vector2 emissionPoint;
    float emissionRate;
    float lifetime;
    
    // Particle properties
    int maxParticles;
    ParticleProperties properties;
    
    // Simulation
    void (*UpdateParticles)(ParticleEntity* self);
    void (*EmitParticle)(ParticleEntity* self);
} ParticleEntity;
```

## Component Types

### Transform Component
```c
typedef struct TransformComponent {
    Component base;
    
    // Local transform
    Vector2 localPosition;
    float localRotation;
    Vector2 localScale;
    
    // World transform
    Vector2 worldPosition;
    float worldRotation;
    Vector2 worldScale;
    
    // Matrix
    Matrix2D localMatrix;
    Matrix2D worldMatrix;
    
    // Methods
    void (*UpdateWorldTransform)(TransformComponent* self);
    void (*SetParent)(TransformComponent* self, Entity* parent);
} TransformComponent;
```

### Renderer Component
```c
typedef struct RendererComponent {
    Component base;
    
    // Render properties
    int sortingLayer;
    int orderInLayer;
    bool castsShadows;
    bool receiveShadows;
    
    // Materials
    Material* material;
    Material** materials;
    int materialCount;
    
    // Methods
    void (*Render)(RendererComponent* self);
    void (*UpdateBounds)(RendererComponent* self);
} RendererComponent;
```

### Physics Component
```c
typedef struct PhysicsComponent {
    Component base;
    
    // Physics body
    PhysicsBody* body;
    PhysicsShape shape;
    
    // Properties
    float mass;
    float friction;
    float restitution;
    bool isTrigger;
    
    // Collision handling
    void (*OnCollisionEnter)(PhysicsComponent* self, Collision* collision);
    void (*OnCollisionExit)(PhysicsComponent* self, Collision* collision);
} PhysicsComponent;
```

## Entity Management

### Entity Factory
```c
typedef struct EntityFactory {
    // Creation methods
    Entity* (*CreateEntity)(const char* name);
    GameObject* (*CreateGameObject)(const char* name);
    UIEntity* (*CreateUIElement)(const char* name);
    
    // Prefab system
    Entity* (*InstantiatePrefab)(const char* prefabId);
    void (*SavePrefab)(Entity* entity, const char* prefabId);
    
    // Pool system
    EntityPool* (*CreatePool)(const char* prefabId, int initialSize);
    Entity* (*GetFromPool)(EntityPool* pool);
    void (*ReturnToPool)(EntityPool* pool, Entity* entity);
} EntityFactory;
```

### Entity Manager
```c
typedef struct EntityManager {
    // Entity tracking
    Entity** entities;
    int entityCount;
    int capacity;
    
    // Entity queries
    Entity* (*FindByName)(const char* name);
    Entity** (*FindByTag)(uint32_t tag, int* count);
    Entity** (*FindByLayer)(uint32_t layer, int* count);
    
    // Updates
    void (*UpdateEntities)(void);
    void (*LateUpdateEntities)(void);
    void (*CleanupEntities)(void);
} EntityManager;
```

## Debug Features

### Entity Inspector
```c
void InspectEntity(Entity* entity) {
    // Display entity info
    DrawEntityInfo(entity);
    
    // Display components
    DrawComponentList(entity);
    
    // Display hierarchy
    DrawEntityHierarchy(entity);
    
    // Display debug gizmos
    DrawEntityGizmos(entity);
}
```

### Component Debug
```c
void DebugComponent(Component* component) {
    // Display component info
    DrawComponentInfo(component);
    
    // Display properties
    DrawComponentProperties(component);
    
    // Display state
    DrawComponentState(component);
    
    // Display events
    DrawComponentEvents(component);
} 