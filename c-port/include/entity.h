#ifndef ENTITY_H
#define ENTITY_H

#include "raylib.h"

// Entity types for the game
typedef enum EntityType {
    ENTITY_NONE = 0,
    ENTITY_PLAYER,
    ENTITY_BALL,
    ENTITY_PADDLE,
    ENTITY_BLOCK,
    ENTITY_POWERUP,
    ENTITY_EFFECT
} EntityType;

// Basic entity structure
typedef struct Entity {
    EntityType type;          // Type of entity
    Rectangle rect;           // Position and size
    Vector2 velocity;         // Velocity for movement
    Color color;              // Color for rendering
    bool active;              // Whether entity is active in the game
    int health;               // Health or hit points
    
    // Function pointers for behavior
    void (*update)(struct Entity* self, float deltaTime);
    void (*draw)(struct Entity* self);
    void (*onCollision)(struct Entity* self, struct Entity* other);
    void (*destroy)(struct Entity* self);
    
    // Additional properties/pointers depending on entity type
    void* data;               // Custom entity-specific data
} Entity;

// Entity pool for memory management
#define MAX_ENTITIES 200
typedef struct EntityPool {
    Entity entities[MAX_ENTITIES];
    int count;
} EntityPool;

// Entity group for handling collections of similar entities
typedef struct EntityGroup {
    Entity** entities;         // Dynamic array of entity pointers
    int count;                 // Number of entities in group
    int capacity;              // Current capacity of the array
} EntityGroup;

// Entity functions
Entity* CreateEntity(EntityType type, Rectangle rect, Vector2 velocity, Color color);
void UpdateEntity(Entity* entity, float deltaTime);
void DrawEntity(Entity* entity);
void DestroyEntity(Entity* entity);
bool CheckEntityCollision(Entity* entity1, Entity* entity2);
void HandleEntityCollision(Entity* entity1, Entity* entity2);

// EntityPool functions
void InitEntityPool(EntityPool* pool);
Entity* AddEntityToPool(EntityPool* pool, EntityType type, Rectangle rect, Vector2 velocity, Color color);
void UpdateEntityPool(EntityPool* pool, float deltaTime);
void DrawEntityPool(EntityPool* pool);
void ClearEntityPool(EntityPool* pool);

// EntityGroup functions
void InitEntityGroup(EntityGroup* group, int initialCapacity);
void AddEntityToGroup(EntityGroup* group, Entity* entity);
void RemoveEntityFromGroup(EntityGroup* group, Entity* entity);
void ClearEntityGroup(EntityGroup* group);
void UpdateEntityGroup(EntityGroup* group, float deltaTime);
void DrawEntityGroup(EntityGroup* group);
void CheckCollisionsInGroup(EntityGroup* group1, EntityGroup* group2);

#endif // ENTITY_H 