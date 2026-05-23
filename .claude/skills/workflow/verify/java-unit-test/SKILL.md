---
name: java-unit-test
description: "为本项目 Spring Boot 模块生成 JUnit 5 + Mockito 单元测试，覆盖 Service 层和 Controller 层。遵循项目已建立的测试规范（@Nested 分组、@DisplayName 中文描述、AssertJ 断言、standalone MockMvc）。"
---

# Java Unit Test 生成工作流

## 适用场景

- 为新写的 Service / Controller 补充单元测试
- 为现有代码生成缺失的测试用例
- 触发方式：`/java-unit-test [目标类路径 或 模块名]`

---

## 工作流

### Phase 1 — 分析目标

**读取以下内容（全部，不跳过）**：

1. 目标 Service 接口 + ServiceImpl（每个方法的完整逻辑）
2. 目标 Controller（每个端点的参数校验、返回值、异常路径）
3. 所有依赖类型：Mapper、RedisTemplate、第三方 Client（如 AliyunCloudAuthClient）
4. DTO Request（`@NotBlank`、`@NotNull` 等校验注解）
5. DTO Response（工厂方法：`success()`、`fail()`、`pending()` 等）

**分析要点**：
- 每个 public 方法有哪些分支？（条件判断 → 测试用例）
- 抛出异常的条件？（每条 `throw` → 一个负向用例）
- 外部依赖（Mapper、Redis、第三方 API）的返回值影响？
- Redis 依赖模式：`redisTemplate.opsForValue().get/set/delete`

---

### Phase 2 — 制定测试用例清单

输出格式：

```
目标: {ClassName}

Service 层测试 ({MethodName}):
  [happy] {方法名}_成功场景描述
  [error] {方法名}_失败条件 → 期望抛出 RuntimeException("xxx")
  [edge]  {方法名}_边界条件描述

Controller 层测试 (POST/GET /path):
  [happy] 正常请求 → HTTP 200, data.xxx 正确
  [valid] 缺少必填字段 xxx → HTTP 400
  [error] Service 抛异常 → HTTP 500
```

**等待确认后再生成代码**（除非用户说"直接生成"）。

---

### Phase 3 — 生成测试文件

#### 3.1 Service 层测试规范

**技术**：JUnit 5 + Mockito，**无 Spring 上下文**

```java
@ExtendWith(MockitoExtension.class)
@DisplayName("{ClassName} 单元测试")
class {ClassName}Test {

    // Mock 所有依赖
    @Mock private XxxMapper xxxMapper;
    @Mock private RedisTemplate<String, Object> redisTemplate;
    @Mock private ValueOperations<String, Object> valueOperations;

    @InjectMocks
    private {ClassName} service;

    @BeforeEach
    void setUp() {
        // Redis 必须在 setUp 中预设
        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
    }

    @Nested
    @DisplayName("{methodName} - 方法描述")
    class MethodName {

        @Test
        @DisplayName("正常场景：xxx 时返回 yyy")
        void happyPath_description() {
            // Arrange
            when(xxxMapper.selectOne(any())).thenReturn(buildEntity());

            // Act
            XxxResponse result = service.method(buildRequest());

            // Assert
            assertThat(result.getXxx()).isEqualTo("expected");
            verify(xxxMapper).insert(any(XxxEntity.class));
        }

        @Test
        @DisplayName("异常场景：xxx 不存在时抛出异常")
        void errorPath_xxxNotFound_throwsException() {
            when(xxxMapper.selectOne(any())).thenReturn(null);

            assertThatThrownBy(() -> service.method(buildRequest()))
                    .isInstanceOf(RuntimeException.class)
                    .hasMessageContaining("xxx不存在");
        }
    }

    // ========== 辅助方法 ==========
    private XxxRequest buildRequest() { ... }
    private XxxEntity buildEntity() { ... }
}
```

**必须覆盖的场景**：
- 每条 `if (xxx == null) throw` → 一个 `@Test`
- 每条 `if (!condition) throw` → 一个 `@Test`
- 每个 `verify(mapper).insert / updateById` → 对应 `@Test`
- Redis key 读写验证：`verify(valueOperations, times(N)).set(...)`
- 数据库写入字段验证：`ArgumentCaptor` 捕获后断言关键字段

#### 3.2 Controller 层测试规范

**技术**：JUnit 5 + Mockito + **standalone MockMvc**（不加载 Spring 上下文，绕过 Security/AOP）

```java
@ExtendWith(MockitoExtension.class)
@DisplayName("{ControllerName} 单元测试")
class {ControllerName}Test {

    private MockMvc mockMvc;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Mock private XxxService xxxService;

    @InjectMocks
    private {ControllerName} controller;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.standaloneSetup(controller).build();
    }

    @Nested
    @DisplayName("POST /api/xxx/yyy - 操作名")
    class PostXxx {

        @Test
        @DisplayName("正常请求，返回 data.certifyId 和 certifyUrl")
        void success() throws Exception {
            when(xxxService.method(any())).thenReturn(buildResponse());

            mockMvc.perform(post("/api/xxx/yyy")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(buildRequest())))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.code").value(200))
                    .andExpect(jsonPath("$.data.fieldName").value("expected"));
        }

        @Test
        @DisplayName("必填字段 xxx 为空 → 400")
        void missingXxx_returns400() throws Exception {
            XxxRequest req = buildRequest();
            req.setXxx("");  // 触发 @NotBlank

            mockMvc.perform(post("/api/xxx/yyy")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(req)))
                    .andExpect(status().isBadRequest());
        }
    }
}
```

**必须覆盖的场景**：
- 每个 `@NotBlank` / `@NotNull` 字段 → 一个空值 400 测试
- 请求体为 `{}` → 400（触发所有 required 字段校验）
- Service 正常返回 → 断言 JSON 路径
- Service 抛出异常 → `status().isInternalServerError()`

---

### Phase 4 — 第三方 SDK 响应对象构造规范

#### 阿里云 Tea SDK（cloudauth20190307）

**关键规则**：`Body` 类是**顶层类**，不是 `Response` 的嵌套类。

```java
// ✅ 正确
import com.aliyun.cloudauth20190307.models.InitFaceVerifyResponseBody;

private InitFaceVerifyResponse buildInitResponse(String certifyId, String certifyUrl) {
    InitFaceVerifyResponse response = new InitFaceVerifyResponse();
    response.body = new InitFaceVerifyResponseBody();
    response.body.code = "200";
    response.body.resultObject =
            new InitFaceVerifyResponseBody.InitFaceVerifyResponseBodyResultObject();
    response.body.resultObject.certifyId = certifyId;
    response.body.resultObject.certifyUrl = certifyUrl;
    return response;
}

// ❌ 错误（编译失败）
response.body = new InitFaceVerifyResponse.InitFaceVerifyResponseBody(); // 不存在
```

**验证 SDK 嵌套结构的方法**（如遇编译失败）：
```bash
jar tf ~/.m2/repository/com/aliyun/{artifactId}/{version}/*.jar | grep -i "ResponseBody"
javap -p ~/.m2/repository/.../xxxResponseBody.class
```

---

### Phase 5 — 运行测试

**此项目为非标准多模块项目（父 pom 无 `<modules>` 声明），使用 `-f` 参数**：

```bash
# 运行指定模块全部测试
mvn test -f modules/{module-name}/pom.xml

# 运行单个测试类
mvn test -f modules/{module-name}/pom.xml -Dtest={TestClassName}

# 依赖未安装时先 install
mvn install -f modules/generic-orm-archetype/pom.xml -DskipTests
mvn install -f modules/systemmanagement/pom.xml -DskipTests
mvn test -f modules/{module-name}/pom.xml
```

---

### Phase 6 — 修复失败

常见错误及修复方式：

| 错误 | 原因 | 修复 |
|------|------|------|
| `找不到符号: 类 XxxResponseBody 位置: 类 XxxResponse` | Body 类是顶层类，不是 Response 嵌套类 | 用 `jar tf` 确认实际包路径，单独 import |
| `NullPointerException in @BeforeEach` | Redis mock 未初始化 | 确保 `when(redisTemplate.opsForValue()).thenReturn(valueOperations)` 在 `@BeforeEach` 中 |
| `Could not find the selected project in the reactor` | 使用了 `-pl` 但父 pom 无 `<modules>` | 改用 `-f modules/{name}/pom.xml` |
| `UnnecessaryStubbingException` | 某条 `when(...)` 在测试中未被调用 | 移除多余 mock，或加 `@MockitoSettings(strictness = LENIENT)` |
| HTTP 400 未按预期触发 | standalone MockMvc 未配置 Validator | 加 `.setValidator(Validation.buildDefaultValidatorFactory().getValidator())` |

---

## 文件命名规范

```
src/test/java/{包路径}/
├── service/impl/{ServiceImpl}Test.java    # Service 层测试
└── controller/{Controller}Test.java       # Controller 层测试
```

---

## 检查清单

生成后确认：
- [ ] 每个 public 方法都有 `@Nested` 分组
- [ ] 每条 `throw` 路径有对应负向测试
- [ ] `@BeforeEach` 中初始化了 Redis mock（如有）
- [ ] Controller 测试用 `standaloneSetup`（非 `@WebMvcTest`）
- [ ] 第三方 SDK Body 类 import 路径正确（顶层类）
- [ ] `verify()` 验证了关键写操作（insert/updateById/delete）
- [ ] 关键写入字段用 `ArgumentCaptor` 断言

---

## 参考实现

本项目已有的测试范例：
- `modules/realname-auth/src/test/.../RealNameAuthServiceImplTest.java` — Service 层完整范例
- `modules/realname-auth/src/test/.../RealNameAuthControllerTest.java` — Controller 层完整范例

---

## 覆盖率目标

| 代码类型 | 最低覆盖率 | AI 生成 | 人工补充 |
|----------|-----------|---------|----------|
| 核心业务逻辑 | ≥ 80% | ✅ 基础用例 | 边界场景 |
| 工具类/DTO | ≥ 60% | ✅ 完整 | - |
| 整体项目 | ≥ 70% | - | - |

## AI vs 人工职责边界

| 类别 | AI 生成 | 人工补充 |
|------|---------|----------|
| 正常路径 | ✅ Happy path + 基本断言 | - |
| 异常分支 | ✅ `throw` 路径 | 并发/竞态条件 |
| 边界值 | ⚠️ 基本边界 | 极端值、特殊场景 |
| 性能测试 | ❌ | 必须人工编写 |
| 集成测试 | ❌ | 必须人工编写 |

**输出约定**：生成测试后，明确列出需要人工补充的项：

```markdown
## 人工补充建议

以下场景建议人工补充测试：
- [ ] 并发场景：[具体场景]
- [ ] 边界值：[具体边界]
- [ ] 性能测试：[具体指标]
```
