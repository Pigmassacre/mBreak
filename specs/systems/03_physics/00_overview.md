# Physics System Overview

## System Components

### Physics World
```c
typedef struct PhysicsWorld {
    // World properties
    Vector2 gravity;
    float timeStep;
    int velocityIterations;
    int positionIterations;
    
    // Collision layers
    uint32_t collisionMask;
    CollisionLayer* layers;
    int layerCount;
    
    // Bodies and joints
    PhysicsBody** bodies;
    int bodyCount;
    int bodyCapacity;
    
    PhysicsJoint** joints;
    int jointCount;
    int jointCapacity;
    
    // Broad phase
    QuadTree* broadPhase;
    
    // Debug
    bool debugDraw;
} PhysicsWorld;
```

### Physics Body
```c
typedef struct PhysicsBody {
    // Core properties
    BodyType type;          // STATIC, KINEMATIC, DYNAMIC
    float mass;
    float inertia;
    float restitution;
    float friction;
    
    // State
    Vector2 position;
    float rotation;
    Vector2 velocity;
    float angularVelocity;
    
    // Forces
    Vector2 force;
    float torque;
    
    // Collision
    CollisionShape shape;
    uint32_t categoryBits;
    uint32_t maskBits;
    
    // User data
    void* userData;
} PhysicsBody;
```

### Collision Shape
```c
typedef struct CollisionShape {
    ShapeType type;     // CIRCLE, RECTANGLE, POLYGON
    
    union {
        struct {
            float radius;
        } circle;
        
        struct {
            float width;
            float height;
        } rectangle;
        
        struct {
            Vector2* vertices;
            int vertexCount;
        } polygon;
    } data;
} CollisionShape;
```

## Core Features

### Body Management
```c
PhysicsBody* CreateBody(PhysicsWorld* world, BodyDef* def) {
    // Allocate body
    PhysicsBody* body = AllocateBody(world);
    if (!body) return NULL;
    
    // Initialize properties
    body->type = def->type;
    body->position = def->position;
    body->rotation = def->rotation;
    body->mass = def->mass;
    body->inertia = CalculateInertia(def);
    
    // Setup collision
    body->shape = def->shape;
    body->categoryBits = def->categoryBits;
    body->maskBits = def->maskBits;
    
    // Add to world
    AddBodyToWorld(world, body);
    
    return body;
}
```

### Physics Step
```c
void StepPhysics(PhysicsWorld* world, float deltaTime) {
    // Update broad phase
    UpdateBroadPhase(world);
    
    // Generate collision pairs
    CollisionPair* pairs = GenerateCollisionPairs(world);
    
    // Solve velocities
    for (int i = 0; i < world->velocityIterations; i++) {
        SolveVelocities(world, pairs);
    }
    
    // Integrate forces
    IntegrateForces(world, deltaTime);
    
    // Solve positions
    for (int i = 0; i < world->positionIterations; i++) {
        SolvePositions(world, pairs);
    }
    
    // Clear forces
    ClearForces(world);
}
```

### Collision Detection
```c
void DetectCollisions(PhysicsWorld* world, CollisionPair* pairs) {
    for (int i = 0; i < pairs->count; i++) {
        PhysicsBody* bodyA = pairs->bodies[i][0];
        PhysicsBody* bodyB = pairs->bodies[i][1];
        
        // Skip if masks don't match
        if (!(bodyA->categoryBits & bodyB->maskBits) ||
            !(bodyB->categoryBits & bodyA->maskBits)) {
            continue;
        }
        
        // Perform narrow phase collision
        Contact contact;
        if (TestCollision(bodyA, bodyB, &contact)) {
            // Add contact to solver
            AddContact(world, &contact);
            
            // Trigger collision callbacks
            TriggerCollisionCallbacks(bodyA, bodyB, &contact);
        }
    }
}
```

## Constraint System

### Joint Types
```c
typedef struct PhysicsJoint {
    JointType type;    // DISTANCE, REVOLUTE, PRISMATIC
    
    PhysicsBody* bodyA;
    PhysicsBody* bodyB;
    
    bool collideConnected;
    
    union {
        struct {
            float length;
            float frequency;
            float damping;
        } distance;
        
        struct {
            Vector2 anchor;
            float lowerAngle;
            float upperAngle;
            float maxTorque;
        } revolute;
        
        struct {
            Vector2 axis;
            float lowerTranslation;
            float upperTranslation;
            float maxForce;
        } prismatic;
    } def;
} PhysicsJoint;
```

### Constraint Solver
```c
void SolveConstraints(PhysicsWorld* world) {
    // Prepare constraints
    PrepareConstraints(world);
    
    // Solve velocity constraints
    for (int i = 0; i < world->velocityIterations; i++) {
        for (int j = 0; j < world->jointCount; j++) {
            SolveJointVelocity(world->joints[j]);
        }
    }
    
    // Solve position constraints
    for (int i = 0; i < world->positionIterations; i++) {
        for (int j = 0; j < world->jointCount; j++) {
            SolveJointPosition(world->joints[j]);
        }
    }
}
```

## Optimization

### Broad Phase
```c
void UpdateBroadPhase(PhysicsWorld* world) {
    // Clear quadtree
    ClearQuadTree(world->broadPhase);
    
    // Insert all bodies
    for (int i = 0; i < world->bodyCount; i++) {
        PhysicsBody* body = world->bodies[i];
        AABB bounds = CalculateAABB(body);
        
        // Insert into quadtree
        InsertBody(world->broadPhase, body, bounds);
    }
}

CollisionPair* QueryBroadPhase(PhysicsWorld* world, PhysicsBody* body) {
    // Calculate query AABB
    AABB bounds = CalculateAABB(body);
    
    // Query quadtree
    return QueryQuadTree(world->broadPhase, bounds);
}
```

### Island Solver
```c
void SolveIslands(PhysicsWorld* world) {
    // Build islands
    Island* islands = BuildIslands(world);
    
    // Solve each island
    for (int i = 0; i < islands->count; i++) {
        Island* island = &islands[i];
        
        // Solve velocities
        for (int j = 0; j < world->velocityIterations; j++) {
            SolveIslandVelocities(island);
        }
        
        // Solve positions
        for (int j = 0; j < world->positionIterations; j++) {
            SolveIslandPositions(island);
        }
    }
}
```

## Debug Features

### Debug Draw
```c
void DrawPhysicsDebug(PhysicsWorld* world) {
    if (!world->debugDraw) return;
    
    // Draw shapes
    for (int i = 0; i < world->bodyCount; i++) {
        DrawBody(world->bodies[i]);
    }
    
    // Draw joints
    for (int i = 0; i < world->jointCount; i++) {
        DrawJoint(world->joints[i]);
    }
    
    // Draw broad phase
    DrawQuadTree(world->broadPhase);
    
    // Draw contacts
    DrawContacts(world);
}
```

### Performance Profiling
```c
void ProfilePhysics(PhysicsWorld* world) {
    // Profile broad phase
    ProfileBroadPhase();
    
    // Profile narrow phase
    ProfileNarrowPhase();
    
    // Profile constraint solver
    ProfileConstraintSolver();
    
    // Profile integration
    ProfileIntegration();
    
    // Generate report
    GeneratePhysicsProfile();
}
``` 