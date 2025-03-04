# Utilities Overview

## Math Utilities

### Vector Operations
```c
typedef struct Vector2Utils {
    // Basic operations
    Vector2 (*Add)(Vector2 v1, Vector2 v2);
    Vector2 (*Subtract)(Vector2 v1, Vector2 v2);
    Vector2 (*Multiply)(Vector2 v, float scalar);
    Vector2 (*Divide)(Vector2 v, float scalar);
    
    // Vector math
    float (*Length)(Vector2 v);
    float (*Distance)(Vector2 v1, Vector2 v2);
    float (*Angle)(Vector2 v);
    Vector2 (*Normalize)(Vector2 v);
    
    // Advanced operations
    Vector2 (*Rotate)(Vector2 v, float angle);
    Vector2 (*Lerp)(Vector2 start, Vector2 end, float t);
    Vector2 (*Reflect)(Vector2 v, Vector2 normal);
} Vector2Utils;
```

### Math Functions
```c
typedef struct MathUtils {
    // Angle operations
    float (*DegToRad)(float degrees);
    float (*RadToDeg)(float radians);
    float (*WrapAngle)(float angle);
    
    // Interpolation
    float (*Lerp)(float start, float end, float t);
    float (*SmoothStep)(float start, float end, float t);
    float (*EaseIn)(float t, float power);
    float (*EaseOut)(float t, float power);
    
    // Random
    float (*Random)(float min, float max);
    int (*RandomInt)(int min, int max);
    bool (*RandomBool)(float probability);
    Vector2 (*RandomVector)(Rectangle bounds);
} MathUtils;
```

## String Utilities

### String Operations
```c
typedef struct StringUtils {
    // Basic operations
    char* (*Copy)(const char* str);
    char* (*Concat)(const char* str1, const char* str2);
    char* (*SubString)(const char* str, int start, int length);
    
    // Formatting
    char* (*Format)(const char* format, ...);
    char* (*TrimWhitespace)(const char* str);
    char* (*ToLower)(const char* str);
    char* (*ToUpper)(const char* str);
    
    // Parsing
    int (*ToInt)(const char* str);
    float (*ToFloat)(const char* str);
    bool (*ToBool)(const char* str);
    
    // Search
    bool (*Contains)(const char* str, const char* search);
    int (*FindFirst)(const char* str, const char* search);
    int (*FindLast)(const char* str, const char* search);
} StringUtils;
```

### Text Processing
```c
typedef struct TextUtils {
    // Word processing
    char** (*SplitWords)(const char* text, int* count);
    char* (*JoinWords)(char** words, int count, const char* separator);
    
    // Line processing
    char** (*SplitLines)(const char* text, int* count);
    char* (*JoinLines)(char** lines, int count);
    
    // Text wrapping
    char* (*WrapText)(const char* text, int width);
    char* (*TruncateText)(const char* text, int maxLength);
} TextUtils;
```

## File Utilities

### File Operations
```c
typedef struct FileUtils {
    // Basic operations
    bool (*Exists)(const char* path);
    bool (*Delete)(const char* path);
    bool (*Copy)(const char* source, const char* dest);
    bool (*Move)(const char* source, const char* dest);
    
    // Directory operations
    bool (*CreateDir)(const char* path);
    bool (*DeleteDir)(const char* path);
    char** (*ListFiles)(const char* path, const char* extension, int* count);
    
    // File reading
    char* (*ReadTextFile)(const char* path);
    unsigned char* (*ReadBinaryFile)(const char* path, size_t* size);
    char** (*ReadLines)(const char* path, int* count);
    
    // File writing
    bool (*WriteTextFile)(const char* path, const char* text);
    bool (*WriteBinaryFile)(const char* path, const unsigned char* data, size_t size);
    bool (*WriteLines)(const char* path, char** lines, int count);
} FileUtils;
```

### Path Operations
```c
typedef struct PathUtils {
    // Path components
    char* (*GetDirectory)(const char* path);
    char* (*GetFilename)(const char* path);
    char* (*GetExtension)(const char* path);
    
    // Path manipulation
    char* (*Combine)(const char* path1, const char* path2);
    char* (*GetAbsolute)(const char* path);
    char* (*GetRelative)(const char* path, const char* basePath);
    
    // Path validation
    bool (*IsAbsolute)(const char* path);
    bool (*IsDirectory)(const char* path);
    bool (*HasExtension)(const char* path, const char* extension);
} PathUtils;
```

## Debug Utilities

### Logging
```c
typedef struct LogUtils {
    // Log levels
    void (*Info)(const char* format, ...);
    void (*Warning)(const char* format, ...);
    void (*Error)(const char* format, ...);
    void (*Debug)(const char* format, ...);
    
    // Log configuration
    void (*SetLogLevel)(LogLevel level);
    void (*SetLogFile)(const char* path);
    void (*SetLogCallback)(LogCallback callback);
    
    // Log analysis
    void (*StartLogGroup)(const char* name);
    void (*EndLogGroup)(void);
    void (*DumpLogToFile)(const char* path);
} LogUtils;
```

### Performance Monitoring
```c
typedef struct PerfUtils {
    // Timing
    void (*StartTimer)(const char* name);
    void (*StopTimer)(const char* name);
    float (*GetElapsedTime)(const char* name);
    
    // Memory tracking
    void (*TrackAllocation)(size_t size, const char* tag);
    void (*TrackDeallocation)(size_t size, const char* tag);
    size_t (*GetTotalAllocated)(const char* tag);
    
    // Performance reporting
    void (*GenerateReport)(void);
    void (*SaveReportToFile)(const char* path);
} PerfUtils;
```

## Data Structures

### Dynamic Array
```c
typedef struct DynArray {
    // Core operations
    void (*Init)(DynArray* array, size_t elementSize);
    void (*Add)(DynArray* array, const void* element);
    void (*Remove)(DynArray* array, size_t index);
    void (*Clear)(DynArray* array);
    
    // Access
    void* (*Get)(DynArray* array, size_t index);
    void (*Set)(DynArray* array, size_t index, const void* element);
    size_t (*GetSize)(DynArray* array);
    
    // Memory management
    void (*Reserve)(DynArray* array, size_t capacity);
    void (*Shrink)(DynArray* array);
} DynArray;
```

### Hash Table
```c
typedef struct HashTable {
    // Core operations
    void (*Init)(HashTable* table, size_t keySize, size_t valueSize);
    void (*Set)(HashTable* table, const void* key, const void* value);
    bool (*Get)(HashTable* table, const void* key, void* value);
    bool (*Remove)(HashTable* table, const void* key);
    
    // Iteration
    void (*ForEach)(HashTable* table, HashTableCallback callback);
    void* (*GetKeys)(HashTable* table, size_t* count);
    void* (*GetValues)(HashTable* table, size_t* count);
    
    // Statistics
    size_t (*GetSize)(HashTable* table);
    float (*GetLoadFactor)(HashTable* table);
} HashTable;
``` 