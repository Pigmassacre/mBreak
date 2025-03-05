#include "entity.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// Entity functions implementation

Entity* CreateEntity(EntityType type, Rectangle rect, Vector2 velocity, Color color) {
    Entity* entity = (Entity*)malloc(sizeof(Entity));
    if (!entity) {
        printf("Error: Failed to allocate memory for entity\n");
        return NULL;
    }
    
    entity->type = type;
    entity->rect = rect;
    entity->velocity = velocity;
    entity->color = color;
    entity->active = true;
    entity->health = 1;
    entity->update = NULL;
    entity->draw = NULL;
    entity->onCollision = NULL;
    entity->destroy = NULL;
    entity->data = NULL;
    
    return entity;
}

void UpdateEntity(Entity* entity, float deltaTime) {
    if (!entity || !entity->active) return;
    
    // Call the entity's update function if it exists
    if (entity->update) {
        entity->update(entity, deltaTime);
    } else {
        // Default update behavior
        entity->rect.x += entity->velocity.x * deltaTime;
        entity->rect.y += entity->velocity.y * deltaTime;
    }
}

void DrawEntity(Entity* entity) {
    if (!entity || !entity->active) return;
    
    // Call the entity's draw function if it exists
    if (entity->draw) {
        entity->draw(entity);
    } else {
        // Default draw behavior
        DrawRectangleRec(entity->rect, entity->color);
    }
}

void DestroyEntity(Entity* entity) {
    if (!entity) return;
    
    // Call the entity's destroy function if it exists
    if (entity->destroy) {
        entity->destroy(entity);
    }
    
    // Free any entity-specific data if it exists
    if (entity->data) {
        free(entity->data);
    }
    
    free(entity);
}

bool CheckEntityCollision(Entity* entity1, Entity* entity2) {
    if (!entity1 || !entity2 || !entity1->active || !entity2->active) return false;
    
    return CheckCollisionRecs(entity1->rect, entity2->rect);
}

void HandleEntityCollision(Entity* entity1, Entity* entity2) {
    if (!entity1 || !entity2 || !entity1->active || !entity2->active) return;
    
    // Call the entities' collision functions if they exist
    if (entity1->onCollision) {
        entity1->onCollision(entity1, entity2);
    }
    
    if (entity2->onCollision) {
        entity2->onCollision(entity2, entity1);
    }
}

// EntityPool functions implementation

void InitEntityPool(EntityPool* pool) {
    if (!pool) return;
    
    memset(pool->entities, 0, sizeof(Entity) * MAX_ENTITIES);
    pool->count = 0;
}

Entity* AddEntityToPool(EntityPool* pool, EntityType type, Rectangle rect, Vector2 velocity, Color color) {
    if (!pool || pool->count >= MAX_ENTITIES) return NULL;
    
    Entity* entity = &pool->entities[pool->count];
    entity->type = type;
    entity->rect = rect;
    entity->velocity = velocity;
    entity->color = color;
    entity->active = true;
    entity->health = 1;
    entity->update = NULL;
    entity->draw = NULL;
    entity->onCollision = NULL;
    entity->destroy = NULL;
    entity->data = NULL;
    
    pool->count++;
    
    return entity;
}

void UpdateEntityPool(EntityPool* pool, float deltaTime) {
    if (!pool) return;
    
    for (int i = 0; i < pool->count; i++) {
        UpdateEntity(&pool->entities[i], deltaTime);
    }
}

void DrawEntityPool(EntityPool* pool) {
    if (!pool) return;
    
    for (int i = 0; i < pool->count; i++) {
        DrawEntity(&pool->entities[i]);
    }
}

void ClearEntityPool(EntityPool* pool) {
    if (!pool) return;
    
    for (int i = 0; i < pool->count; i++) {
        if (pool->entities[i].destroy) {
            pool->entities[i].destroy(&pool->entities[i]);
        }
        
        if (pool->entities[i].data) {
            free(pool->entities[i].data);
        }
    }
    
    memset(pool->entities, 0, sizeof(Entity) * MAX_ENTITIES);
    pool->count = 0;
}

// EntityGroup functions implementation

void InitEntityGroup(EntityGroup* group, int initialCapacity) {
    if (!group) return;
    
    group->entities = (Entity**)malloc(sizeof(Entity*) * initialCapacity);
    if (!group->entities) {
        printf("Error: Failed to allocate memory for entity group\n");
        return;
    }
    
    group->count = 0;
    group->capacity = initialCapacity;
}

void AddEntityToGroup(EntityGroup* group, Entity* entity) {
    if (!group || !entity) return;
    
    // Resize the array if necessary
    if (group->count >= group->capacity) {
        int newCapacity = group->capacity * 2;
        Entity** newEntities = (Entity**)realloc(group->entities, sizeof(Entity*) * newCapacity);
        if (!newEntities) {
            printf("Error: Failed to resize entity group\n");
            return;
        }
        
        group->entities = newEntities;
        group->capacity = newCapacity;
    }
    
    group->entities[group->count] = entity;
    group->count++;
}

void RemoveEntityFromGroup(EntityGroup* group, Entity* entity) {
    if (!group || !entity) return;
    
    // Find the entity in the group
    int index = -1;
    for (int i = 0; i < group->count; i++) {
        if (group->entities[i] == entity) {
            index = i;
            break;
        }
    }
    
    // If the entity was found, remove it
    if (index != -1) {
        // Shift all entities after it down by one
        for (int i = index; i < group->count - 1; i++) {
            group->entities[i] = group->entities[i + 1];
        }
        
        group->count--;
    }
}

void ClearEntityGroup(EntityGroup* group) {
    if (!group) return;
    
    free(group->entities);
    group->entities = NULL;
    group->count = 0;
    group->capacity = 0;
}

void UpdateEntityGroup(EntityGroup* group, float deltaTime) {
    if (!group) return;
    
    for (int i = 0; i < group->count; i++) {
        UpdateEntity(group->entities[i], deltaTime);
    }
}

void DrawEntityGroup(EntityGroup* group) {
    if (!group) return;
    
    for (int i = 0; i < group->count; i++) {
        DrawEntity(group->entities[i]);
    }
}

void CheckCollisionsInGroup(EntityGroup* group1, EntityGroup* group2) {
    if (!group1 || !group2) return;
    
    for (int i = 0; i < group1->count; i++) {
        for (int j = 0; j < group2->count; j++) {
            if (CheckEntityCollision(group1->entities[i], group2->entities[j])) {
                HandleEntityCollision(group1->entities[i], group2->entities[j]);
            }
        }
    }
} 
