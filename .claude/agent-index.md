# Agent 角色职能索引（细粒度分组）

> 用途：供 `/compose` 主程序运行时，把「本任务相关角色」喂给架构师做选角。
> 分组维度 = **任务职能**（架构师在任务流里分配的岗位），而非 manifest 的 category（职业身份/技术栈）。
> 原则：分组要细、要全；**允许某些分组暂时缺角色（留空占位，供以后补航天/能源等垂直领域）**。

---

## 0. 说明

- 每个角色标注 `name → 中文名 + 一句话侧重点`，一句话用来区分相邻角色。
- 分类外的 strategy 目录下 16 项（QUICKSTART / EXECUTIVE-BRIEF / handoff-templates / phase-0..6 / scenario-* 等）**不是可选角色，是内部运营文档与流程模板**，不应出现在选角范围内，已在文末单列，禁止喂给架构师。
- 跨组相关时，同一角色以「主归属」为准，个别在括号里标注「兼」。

---

## 1. 研究 / 情报（去外部找事实、搜资料、验证）

- `general-purpose` — 通用搜索：关键词/文件搜索、联网多步检索，无固定领域
- `product-trend-researcher` — 趋势研究员：行业趋势与技术前瞻，未来 6-18 个月方向
- `marketing-daily-news-briefing` — 新闻情报官：多源新闻采集+交叉验证信源，结构化简报
- `marketing-x-twitter-intelligence-analyst` — X/Twitter 情报：社交信号、趋势、账号监测
- `finance-investment-researcher` — 投资研究员：市场研究、尽调、组合分析、资产估值
- `risk-knowledge-retriever` — 知识检索师：从用户本地 Obsidian 库检索，只检索不研判

## 2. 战略 / 商业分析

- `business-strategist` — 商业战略家：竞争分析、市场进入、商业模式、增长规划、战略决策
- `risk-strategy-analyst` — 风控策略：黑灰产识别、作弊防控、风控策略开发与效果评估
- `product-feedback-synthesizer` — 反馈分析：用户反馈收集、分类、洞察提炼
- `specialized-pricing-analyst` — 定价分析师：市场调研、竞品、成本结构、margin 优化
- `specialized-pricing-optimizer` — 动态定价：电商平台价格机制、大促定价、竞品监控
- `product-manager` — 产品经理：产品全生命周期、路线图、GTM、干系人对齐
- `product-sprint-prioritizer` — 需求排序：用框架和数据做优先级，避免拍脑袋
- `support-analytics-reporter` — 数据分析师：原始数据→业务洞察、统计、KPI
- `academic-statistician` — 统计学家：定量方法、实验设计、区分信号与噪声/偶然/偏倚
- `specialized-strategy-duel-agent` — 策略对决推演：博弈论+三十六计实时推演
- `sales-deal-strategist` — 赢单策略：MEDDPICC 资质、复杂 B2B 销售周期规划
- `sales-pipeline-analyst` — Pipeline 分析：单子速度、Forecast 准确度、收入运营

## 3. 财务 / 投融资 / 资本

- `finance-financial-analyst` — 财务分析师：财务建模、预测、场景分析
- `finance-financial-forecaster` — 财务预测：收入预测、现金流、烧钱率、融资对接
- `finance-fpa-analyst` — FP&A：预算、差异分析、滚动预测、战略资源配置
- `chief-financial-officer` — CFO：资本配置、资金运营、财务规划、投资者关系
- `finance-bookkeeper-controller` — 簿记总监：日常会计、对账、结账、内控
- `finance-tax-strategist` — 税务策略：税务优化、多辖区合规、转让定价
- `finance-invoice-manager` — 发票管理：中国发票全生命周期、金税、三单匹配
- `finance-fraud-detector` — 金融风控：交易欺诈、反洗钱、支付渠道风控
- `finance-hk-stock-compliance-reviewer` — 港股合规：HKEX 上市规则、SFC 监管
- `support-finance-tracker` — 财务追踪：财务规划、预算、经营绩效分析
- `sales-data-extraction-agent` — 销售数据提取：从 Excel 提取关键销售指标
- `data-consolidation-agent` — 数据整合：把销售数据整合到报告仪表盘

## 4. AI / 机器学习 / 数据（工程侧）

- `engineering-ai-engineer` — AI 工程师：ML 模型开发到部署全链路工程化
- `engineering-llm-post-training-engineer` — LLM 后训练：SFT、偏好优化、RLHF/RLVR、MoE、发布门禁
- `engineering-rag-pipeline-engineer` — RAG 流水线：分块、检索质量、混合检索、重排序
- `engineering-prompt-engineer` — Prompt 工程：系统提示词架构、CoT、少样本、评测迭代
- `prompt-engineer` — 提示词工程师（偏通用 LLM 提示词打磨，非 Code 专精）【已废弃，见 `engineering-prompt-engineer`】
- `engineering-voice-ai-integration-engineer` — 语音 AI：Whisper/ASR 转录流水线
- `engineering-ai-data-remediation-engineer` — AI 数据修复：SLM 语义聚类自愈数据管道
- `engineering-data-engineer` — 数据工程师：ETL/ELT、Spark、dbt、湖仓、流处理
- `engineering-data-visualization-engineer` — 数据可视化：D3/Vega、诚实编码、色盲安全配色
- `specialized-model-qa` — 模型 QA：端到端审计 ML/统计模型、校准、可解释性
- `gis-spatial-data-scientist` — 空间数据科学：空间统计、聚类、预测
- `gis-geoai-ml-engineer` — GeoAI/ML：卫星/航拍影像特征提取、分割、目标检测

## 5. AI 治理 / 合规 / 政策

- `specialized-ai-policy-writer` — AI 治理政策：中国生成式AI办法、算法备案、安全评估、伦理
- `security-ai-generated-code-auditor` — AI 生成代码审计：硬编码密钥、提示注入、行级安全
- `data-privacy-officer` — 数据隐私官：GDPR/CCPA、数据测绘、同意管理、泄露响应
- `persona-architect` — 人格架构：AI 智能体人格设计、优化、行为建模
- `agentic-identity-trust` — 身份信任：AI 智能体身份认证与信任验证体系
- `specialized-fedramp-rmf-compliance` — FedRAMP/RMF：NIST 800-53、ATO、持续监控
- `engineering-privacy-engineer` — 隐私工程：PII 发现、最小化、DSAR、假名化落地

## 6. 法律 / 合同 / 制度

- `legal-contract-reviewer` — 合同审查：民法典合同编、风险条款、违约金设计
- `legal-document-review` — 法律文书审查：合同/诉讼/不动产摘要、风险标记、版本比对
- `legal-policy-writer` — 制度文件：隐私政策、用户协议、三法合规体系
- `support-legal-compliance-checker` — 法务合规：多辖区法律法规与行业标准
- `specialized-risk-assessor` — 企业风险评估：国企风控、内控 COSO、审计整改、ESG 风险

## 7. 信息与数据治理 / 安全（非合规向）

- `security-architect` — 安全架构：威胁建模、纵深防御、基于风险的设计
- `security-cloud-security-architect` — 云安全：零信任、AWS/Azure/GCP 纵深防御
- `security-appsec-engineer` — AppSec：威胁建模、SAST/DAST、安全代码审查
- `security-penetration-tester` — 渗透测试：红队、漏洞评估、Web/云基础设施
- `security-threat-intelligence-analyst` — 威胁情报：对手团伙追踪、ATT&CK 映射
- `security-threat-detection-engineer` — 检测工程：SIEM 规则、检测即代码
- `security-incident-responder` — 事件响应：数字取证、泄露调查、危机协调
- `security-compliance-auditor` — 安全合规审计：SOC2/ISO27001/HIPAA/PCI-DSS
- `security-senior-secops` — 高级安全运营：密钥泄露、CORS/CSP/限流、安全日志
- `security-blockchain-security-auditor` — 智能合约审计：漏洞检测、形式化验证
- `security-secrets-credential-engineer` — 密钥凭据：全生命周期检测、保管、轮换
- `engineering-security-engineer` — 安全工程师：威胁建模、漏洞评估、应用安全【已废弃，见 `security-appsec-engineer`】
- `engineering-threat-detection-engineer` — 威胁检测（工程侧）：SIEM、狩猎、调优【已废弃，见 `security-threat-detection-engineer`】

## 8. 后端 / 架构 / 系统设计

- `engineering-software-architect` — 软件架构：DDD、架构模式、技术决策
- `engineering-backend-architect` — 后端架构：可扩展系统、数据库、API、云
- `backend-architect-with-memory` — 后端架构（带记忆）：可扩展系统设计（同后端）【已废弃，见 `engineering-backend-architect`】
- `architectural-code-reviewer` — 架构级代码审查：战略级质量、技术债、导师
- `engineering-api-platform-engineer` — API 平台：OpenAPI/gRPC、版本化、网关、SDK
- `engineering-identity-access-engineer` — 身份访问：OAuth/OIDC、SSO、SCIM、RBAC
- `engineering-realtime-collaboration-engineer` — 实时协作：WebSocket/SSE、CRDT/OT
- `engineering-payments-billing-engineer` — 支付计费：PSP 集成、幂等、订阅、PCI
- `identity-graph-operator` — 身份图谱：多智能体共享身份一致性
- `lsp-index-engineer` — LSP 索引：语言服务器协议、语义索引

## 9. 前端 / 移动 / 桌面 / 客户端

- `engineering-frontend-developer` — 前端：React/Vue/Angular、UI 实现、性能
- `engineering-mobile-app-builder` — 移动开发：iOS/Android 原生与跨平台
- `engineering-mobile-release-engineer` — 移动发布：签名、fastlane、商店提交、分阶段发布
- `engineering-desktop-app-engineer` — 桌面应用：Electron/Tauri、IPC、签名、自动更新
- `engineering-wechat-mini-program-developer` — 微信小程序：WXML/WXSS、微信支付、云开发
- `engineering-uswds-developer` — USWDS 前端：美国 Web 设计系统、联邦合规
- `engineering-section-508-specialist` — Section 508：505 无障碍、ARIA、VPAT
- `engineering-i18n-engineer` — 国际化：ICU、CLDR、RTL、伪本地化
- `engineering-pc-host-engineer` — 上位机：Qt/QML、串口、工业协议
- `engineering-senior-developer` — 高级全栈：Laravel/Livewire/FluxUI、Three.js

## 10. 数据存储 / 数据库

- `engineering-database-optimizer` — 数据库优化：Schema、查询、索引、PostgreSQL/MySQL
- `engineering-database-reliability-engineer` — DBRE：高可用、复制、在线迁移、容灾
- `engineering-gaussdb-expert` — GaussDB：华为 OLTP、Ustore、分布式表
- `engineering-search-relevance-engineer` — 搜索相关性：ES/OpenSearch、BM25、混合检索
- `engineering-data-engineer` — 数据工程（兼）：ETL/湖仓（主见第 4 组）

## 11. 云计算 / DevOps / 基础设施 / SRE

- `engineering-devops-automator` — DevOps：CI/CD、基础设施自动化、云运维
- `engineering-sre` — SRE：SLO、错误预算、混沌工程、可观测性
- `sre` — SRE（同义，偏可靠性/事件/可观测性）【已废弃，见 `engineering-sre`】
- `engineering-finops-engineer` — FinOps：云成本分配、缩减、承诺规划、单位经济
- `engineering-autonomous-optimization-architect` — 自主优化：API 影子测试、财务与安全护栏
- `engineering-network-engineer` — 网络：Cisco/Juniper/Palo Alto 路由交换
- `engineering-network-engineer-china` — 国内网络：华为 VRP、华三、锐捷、信创、等保
- `engineering-it-service-manager` — ITSM：ITIL4、服务目录、变更、SLA
- `engineering-incident-response-commander` — 故障响应：生产故障指挥、复盘、SLO 跟踪
- `support-infrastructure-maintainer` — 基础设施运维：可靠性、性能、成本
- `engineering-iot-solution-architect` — IoT 方案：设备接入、边缘、云平台
- `engineering-iot-fleet-engineer` — IoT 设备群：注册、MQTT、OTA、边缘、可观测

## 12. AI/BU 云原生与垂直技术栈

- `engineering-solidity-smart-contract-engineer` — Solidity：EVM、Gas、升级代理、DeFi
- `engineering-rust-refactoring-specialist` — Rust 重构：仓库级重构、panic 加固、clippy
- `engineering-webassembly-engineer` — WebAssembly：Rust/C++/Go 编译 Wasm、组件模型
- `engineering-video-streaming-engineer` — 视频流：HLS/DASH、ffmpeg、DRM、CDN
- `engineering-dingtalk-integration-developer` — 钉钉集成：机器人、审批流、宜搭
- `engineering-feishu-integration-developer` — 飞书集成：机器人、Bitable、Webhook、SSO
- `engineering-email-intelligence-engineer` — 邮件智能：邮件线程结构化提取
- `engineering-cms-developer` — CMS：Drupal/WordPress 主题、插件、内容架构
- `engineering-drupal-performance` / `engineering-drupal-shopping-cart` / `engineering-wordpress-performance` / `engineering-wordpress-shopping-cart` — 各 CMS 性能与电商
- `engineering-filament-optimization-specialist` — Filament：PHP 后台重构优化
- `engineering-orgscript-engineer` — OrgScript：语法设计、AST 校验
- `engineering-embedded-firmware-engineer` — 嵌入式固件：ESP32/STM32/Arduino/Zephyr
- `engineering-embedded-linux-driver-engineer` — 嵌入式 Linux 驱动：内核模块、设备树、Yocto
- `engineering-fpga-digital-design-engineer` — FPGA/ASIC：Verilog/VHDL、AXI、时序收敛
- `engineering-mechanical-design-engineer` — 机械设计：传动/结构件、强度校核、BOM
- `specialized-civil-engineer` — 土木：Eurocode/ACI/GB、结构、岩土

## 13. 开发者体验 / 工具 / 平台

- `engineering-developer-tooling-engineer` — 开发者工具：CLI、内部平台、DX
- `specialized-mcp-builder` — MCP 构建：MCP 服务器、工具/资源/提示词扩展
- `specialized-developer-advocate` — 开发者布道：社区、技术内容、DX
- `engineering-git-workflow-master` — Git 工作流：分支策略、约定式提交、变基
- `engineering-codebase-onboarding-engineer` — 代码库入职引导：读源码、述事实
- `specialized-codebase-archaeologist` — 代码库考古：跨工具漂移检测、死代码
- `engineering-rapid-prototyper` — 快速原型：MVP、概念验证
- `engineering-minimal-change-engineer` — 最小变更：只改要求内、拒绝范围蔓延

## 14. 质量 / 测试 / 代码审查

- `engineering-code-reviewer` — 代码审查：正确性、可维护性、安全、性能
- `engineering-codebase-onboarding-engineer` — （兼，见第 13）
- `testing-api-tester` — API 测试：接口验证、性能、质量
- `testing-test-automation-engineer` — 测试自动化：Playwright/Cypress、稳定选择器
- `testing-performance-benchmarker` — 性能基准：容量规划、基准测试
- `testing-embedded-qa-engineer` — 嵌入式 QA：HIL、固件自动化、故障注入
- `testing-test-results-analyzer` — 测试结果分析：质量度量、洞察
- `testing-tool-evaluator` — 工具评估：功能对比、性能测试、选型
- `testing-reality-checker` — 现实检验：基于证据认证、默认可疑
- `testing-evidence-collector` — 证据收集：测试结论证据链完整性
- `testing-workflow-optimizer` — 流程优化：消除瓶颈、精简流程
- `testing-accessibility-auditor` — 无障碍审核：WCAG、辅助技术实测
- `specialized-model-qa` — 模型 QA（兼，见第 4）
- `analyzer` — 根因分析：调试、排障、系统化问题解决
- `performance` — 性能优化：瓶颈消除、可扩展性、负载测试
- `refactor` — 重构：技术债、代码清理、可维护性

## 15. 设计 / 交互 / 品牌（数字产品）

- `design-ux-architect` — UX 架构：CSS 体系、布局框架、实现指引
- `design-ux-researcher` — UX 研究：用户行为、可用性、数据驱动洞察
- `design-ui-designer` — UI 设计：视觉系统、组件库、像素级界面
- `design-brand-guardian` — 品牌守护：品牌形象、一致性、战略定位
- `design-persona-walkthrough` — Persona 走查：认知走查、CRO 报告
- `design-ui-finish-gate-reviewer` — UI 门禁：拦截通用化 UI、设计契约
- `design-visual-storyteller` — 视觉叙事：复杂信息→视觉故事
- `design-whimsy-injector` — 趣味注入：品牌个性、惊喜细节
- `design-image-prompt-engineer` — 图像提示词：视觉概念→提示词
- `design-inclusive-visuals-specialist` — 包容视觉：消除 AI 图像偏见
- `accessibility` — 无障碍：WCAG、包容性设计、辅助技术
- `product-behavioral-nudge-engine` — 行为助推：交互节奏、动机最大化

## 16. 内容 / 写作 / 翻译 / 报告

- `specialized-report-structurer` — 报告结构化：金字塔原理，零散信息→逻辑严谨报告
- `support-executive-summary-generator` — 高管摘要：SCQA、金字塔、C-level 三分钟决策
- `engineering-technical-writer` — 技术文档：复杂概念→清晰文档
- `specialized-document-generator` — 文档生成：PDF/PPTX/DOCX/XLSX 代码化生成
- `marketing-content-creator` — 内容创作：多平台、多语言讲好故事
- `technical-translator-agent` — 技术翻译：中英技术文档互译
- `language-translator` — 语言翻译：英西互译、文化语境
- `marketing-book-co-author` — 图书协作：语音笔记→结构化章节

## 17. 营销 / 增长 / 获客 / 投放

- `marketing-growth-hacker` — 增长黑客：低成本高回报获客实验
- `marketing-seo-specialist` — SEO：技术 SEO、外链、自然搜索
- `marketing-baidu-seo-specialist` — 百度 SEO：百度算法、生态矩阵、中文关键词
- `marketing-agentic-search-optimizer` — 智能搜索优化：WebMCP、agent 任务完成率
- `marketing-aeo-foundations` — AEO 基础：llms.txt、AI 感知 robots.txt
- `marketing-ai-citation-strategist` — AI 引文：ChatGPT/Claude/Gemini 可见性
- `marketing-email-strategist` — 邮件营销：CRM 序列、生命周期、可送达性
- `marketing-pr-communications-manager` — PR 传播：媒体关系、危机传播、品牌声誉
- `marketing-app-store-optimizer` — ASO：应用商店优化、转化率

## 18. 社交媒体 / 平台运营（分平台）

- `marketing-douyin-strategist` — 抖音：算法、爆款、直播带货
- `marketing-kuaishou-strategist` — 快手：下沉市场、老铁社区、直播电商
- `marketing-tiktok-strategist` — TikTok：病毒、算法、出海
- `marketing-xiaohongshu-operator` / `marketing-xiaohongshu-specialist` — 小红书：种草、达人、爆款公式
- `marketing-wechat-operator` / `marketing-wechat-official-account` — 公众号：内容、私域、小程序
- `marketing-weixin-channels-strategist` — 视频号：社交推荐、直播、私域闭环
- `marketing-weibo-strategist` — 微博：热搜、超话、舆情、粉丝经济
- `marketing-bilibili-strategist` — B站：中长视频、UP主、社区生态
- `marketing-zhihu-strategist` — 知乎：思想领袖、公信力、知识问答
- `marketing-social-media-strategist` — 社媒（LinkedIn/Twitter 职业场景）
- `marketing-linkedin-content-creator` — LinkedIn：个人品牌、职业内容
- `marketing-twitter-engager` — Twitter：实时互动、思想领袖
- `marketing-reddit-community-builder` — Reddit：社区文化、口碑
- `marketing-instagram-curator` — Instagram：视觉叙事、社区运营
- `marketing-podcast-strategist` — 播客：小宇宙/喜马拉雅/苹果播客
- `marketing-global-podcast-strategist` — 全球播客：Spotify/Apple/YouTube
- `marketing-short-video-editing-coach` — 短视频剪辑：剪映/PR/FCP 技术教练
- `marketing-video-optimization-specialist` — 视频优化：YouTube 算法、留存、章节
- `marketing-carousel-growth-engine` — 轮播图增长：Gemini 生成、多平台发布
- `marketing-multi-platform-publisher` — 多平台发布：Wechatsync 路由、草稿优先

## 19. 电商 / 跨境 / 知识付费（变现垂直）

- `marketing-china-ecommerce-operator` — 中国电商：淘宝/天猫/拼多多/京东
- `marketing-cross-border-ecommerce` — 跨境电商：Amazon/Temu/TikTok Shop、合规
- `marketing-livestream-commerce-coach` — 直播电商：话术、选品、付费流
- `marketing-knowledge-commerce-strategist` — 知识付费：得到/知识星球/小鹅通
- `marketing-china-market-localization-strategist` — 中国市场本地化：上市策略
- `marketing-private-domain-operator` — 私域：企微 SCRM、社群、转化漏斗

## 20. 广告 / 付费媒体

- `paid-media-ppc-strategist` — PPC：Google/Microsoft/Amazon 竞价
- `paid-media-programmatic-buyer` — 程序化：DV360、TTD、DSP
- `paid-media-paid-social-strategist` — 社交广告：Meta/LinkedIn/TikTok/Snapchat
- `paid-media-creative-strategist` — 广告创意：文案、RSA、素材测试
- `paid-media-tracking-specialist` — 追踪归因：GTM/GA4/Meta CAPI/服务端
- `paid-media-search-query-analyst` — 搜索词分析：否定关键词、意图映射
- `paid-media-auditor` — 付费媒体审计：账户结构、追踪、竞价 200+ 检查点

## 21. 销售 / 客户成功 / 商务

- `sales-outbound-strategist` — Outbound：多渠道触达、ICP、个性化
- `sales-outreach` — 顾问式外呼：冷线索、异议、方案、管线
- `sales-coach` — 销售教练：Pipeline review、话术辅导、Forecast
- `sales-discovery-coach` — Discovery 教练：问题设计、现状诊断、通话结构
- `sales-proposal-strategist` — 投标策略：RFP、赢标主题、方案
- `sales-account-strategist` — 客户拓展：Land-and-Expand、QBR、NRR
- `sales-engineer` — 售前：技术 Discovery、Demo、POC、竞争定位
- `sales-offer-lead-gen-strategist` — Offer/Lead Gen：价值方程式、lead magnet
- `sales-deal-strategist` — 赢单（兼，见第 2）
- `customer-success-manager` — 客户成功：onboarding、健康分、续约、扩张
- `sales-pipeline-analyst` — Pipeline（兼，见第 2）

## 22. 组织 / 变革 / 人力 / 管理

- `organizational-psychologist` — 组织心理：团队动力、心理安全、倦怠
- `change-management-consultant` — 变革管理：ADKAR、Kotter、Prosci
- `hr-recruiter` — 招聘：Boss/猎聘/拉勾、校招社招全链路
- `hr-onboarding` — HR 入职：员工迎新、文档、留存
- `hr-performance-reviewer` — 绩效：OKR/KPI 双轨、360、校准
- `support-recruitment-specialist` — 招聘运营：渠道运营、劳动法合规
- `operations-manager` — 运营经理：Lean/Six Sigma、产能、KPI、供应商
- `corporate-training-designer` — 企业培训：需求分析、教学设计、领导力
- `project-manager-senior` — 高级 PM：规格拆解、范围控制、经验教训
- `project-management-project-shepherd` — 项目牧羊人：跨部门协调、时间线
- `project-management-studio-producer` — 制片人：创意协调、多项目组合
- `project-management-studio-operations` — 工作室运营：效率、流程、资源
- `technical-pm` — 技术 PM：技术路线图、风险评估、干系人
- `project-management-meeting-notes-specialist` — 会议纪要：决议、action item
- `project-management-jira-workflow-steward` — Jira 管家：提交追溯、PR 规范
- `project-management-experiment-tracker` — 实验追踪：A/B 测试科学管理
- `specialized-meeting-assistant` — 会议效率：纪要、行动项、OKR 周会
- `specialized-chief-of-staff` — 幕僚长：过滤噪音、决策路由
- `ma-integration-manager` — M&A 整合：PMI、百日计划、协同追踪

## 23. 垂直行业 / 场景专家（最需要补全的一组）

**已覆盖：**
- `healthcare-clinical-evidence-agent` — 临床证据：证据标准
- `healthcare-innovation-strategist` — 医疗创新叙事
- `healthcare-sovereign-health-systems-agent` — 健康强制令框架
- `healthcare-customer-service` — 医疗客服
- `healthcare-marketing-compliance` — 医疗营销合规
- `healthcare-aging-parent-care-companion` — 老人照护陪伴
- `medical-billing-coding-specialist` — 医疗账单编码：ICD/CPT/RCM
- `retail-customer-returns` — 零售退货：全渠道退换
- `livestock-archive-auditor` — 养殖档案核对
- `hospitality-guest-services` — 酒店宾客服务：预订、入住、礼宾、投诉
- `accounts-payable-agent` — 应付账款：供应商付款、发票、多支付通道
- `legal-client-intake` — 律所接案：资质审核、案件信息、利益冲突筛查
- `legal-billing-time-tracking` — 律所计费：工时、发票、应收、信托账户
- `grant-writer` — 资助申请：prospect research、proposal、budget narrative
- `report-distribution-agent` — 报告分发：按区域/销售代表分发报告
- `support-support-responder` — 客服响应：多渠道支持、主动关怀
- `supply-chain-strategist` — 供应链采购策略：供应商开发、战略采购、质量管控
- `supply-chain-route-optimizer` — 物流路线：快递/同城/冷链/跨境路线与成本
- `supply-chain-inventory-forecaster` — 库存预测：需求预测、安全库存、补货
- `supply-chain-vendor-evaluator` — 供应商评估：筛选评分、验厂、质量管理
- `supply-chain-garment-factory-planning-engineer` — 服装工厂规划：产线设计、产能测算、精益
- `real-estate-buyer-seller` — 房地产经纪
- `loan-officer-assistant` — 信贷：资格预审、合规
- `study-abroad-advisor` — 留学规划（美英加澳欧港新）
- `gaokao-college-advisor` — 高考志愿填报
- `academic-study-planner` — 学习规划（考研/考公/CPA）
- `specialized-french-consulting-market` — 法国咨询市场（ESN/SI 自由职业）
- `specialized-korean-business-navigator` — 韩国商务文化
- `specialized-cultural-intelligence-strategist` — 文化智能（CQ）
- `government-digital-presales-consultant` — 政务售前：政策、标书、等保密评
- `esg-sustainability-officer` — ESG：披露、脱碳、利益相关方
- `specialized-salesforce-architect` — Salesforce：多云、Governor Limits

**暂时缺角色（留空占位，待补）：**
- 🚀 航天 / 火箭 / 卫星（可复用火箭、轨道动力学、卫星载荷）
- 📡 卫星通信 / 频率轨道资源（ITU 频率、轨道面）
- 🏛 中国航天政策体制（军民融合、星网边界、牌照）
- ⚡ 能源 / 电力 / 新能源
- 🏭 半导体 / 集成电路
- 🚢 海洋 / 航运 / 物流
- 🏥 生物医药 / 制药研发
- 🌾 农业 / 食品
- （…按需扩展）

## 24. 教育 / 写作 / 个人成长

- `academic-psychologist` / `academic-anthropologist` / `academic-historian` / `academic-geographer` / `academic-narratologist` — 学术多学科（设定/世界观/史实/文化，偏创作向）
- `mentor` — 导师：概念讲解、学习指导、教育视角评审
- `personal-growth-mentor` — 个人成长：目标厘清、习惯设计、战略决策
- `zk-steward` — ZK 管家：Luhmann 卡片盒笔记、知识库
- `resume-tailor` — 简历定制：JD 分析、ATS 关键词、改写
- `study-abroad-advisor` / `gaokao-college-advisor` / `academic-study-planner` — （兼，见第 23）

## 25. 游戏 / 3D / 交互娱乐（垂直技术栈）

- `game-designer` — 游戏设计：GDD、玩家心理、经济循环
- `narrative-designer` — 叙事设计：分支对话、世界观
- `level-designer` — 关卡：布局、节奏、遭遇战
- `economy-designer` — 虚拟经济：货币系统、通胀控制
- `game-audio-engineer` — 游戏音频：FMOD/Wwise、自适应音乐
- `technical-artist` — 技术美术：shader、VFX、LOD、性能预算
- `unreal-technical-artist` — Unreal 技术美术：材质、Niagara、程序化内容
- `unreal-multiplayer-architect` — Unreal 多人：Actor 复制、服务端权威、网络预测
- `unreal-systems-engineer` — Unreal 系统：C++/BP 边界、Nanite、Lumen、GAS
- `unreal-world-builder` — Unreal 世界构建：World Partition、Landscape、HLOD
- `unity-editor-tool-developer` — Unity 编辑器工具：EditorWindow、管线自动化
- `unity-shader-graph-artist` — Unity Shader：Shader Graph、HLSL、URP/HDRP
- `unity-multiplayer-engineer` — Unity 多人：Netcode、Relay/Lobby、状态同步
- `unity-architect` — Unity 架构：ScriptableObject、解耦、单一职责
- `godot-gameplay-scripter` — Godot 脚本：GDScript 2.0、C#、节点式架构
- `godot-shader-developer` — Godot Shader：着色语言、VisualShader、后处理
- `godot-multiplayer-engineer` — Godot 多人：MultiplayerAPI、ENet/WebRTC
- `roblox-experience-designer` — Roblox 体验：参与循环、DataStore、变现
- `roblox-systems-scripter` — Roblox 系统：Luau、安全模型、RemoteEvent
- `roblox-avatar-creator` — Roblox 形象：UGC、配件绑定、纹理标准
- `blender-addon-engineer` — Blender 插件：资源验证、管线自动化

## 26. GIS / 地理空间 / 测绘

- `gis-analyst` — GIS 分析师：制图、图层、空间查询
- `gis-spatial-data-engineer` — 空间数据工程：ETL、重投影、归一化
- `gis-spatial-data-scientist` — 空间数据科学（兼，见第 4）
- `gis-geoai-ml-engineer` — GeoAI/ML（兼，见第 4）
- `gis-cartography-designer` — 制图设计：配色、字体、注记
- `gis-web-gis-developer` — Web GIS：MapLibre/ArcGIS JS/Leaflet
- `gis-3d-scene-developer` — 三维场景：Cesium、点云
- `gis-drone-reality-mapping` — 无人机实景：摄影测量、正射影像
- `gis-bim-specialist` — BIM/GIS：Revit/IFC、数字孪生
- `gis-geoprocessing-specialist` — 地理处理：ArcPy 工具箱、批量自动化
- `gis-qa-engineer` — GIS 质检：拓扑、元数据、CRS
- `gis-technical-consultant` — GIS 顾问：差距分析、路线图、RFP
- `gis-solution-engineer` — GIS 方案：POC、Esri 与开源栈

## 27. 空间计算 / XR / 终端

- `xr-interface-architect` — XR 界面：空间交互、界面策略
- `xr-immersive-developer` — XR 开发：WebXR、浏览器 AR/VR
- `xr-cockpit-interaction-specialist` — XR 座舱：沉浸式座舱控制
- `visionos-spatial-engineer` — visionOS：SwiftUI、Liquid Glass
- `macos-spatial-metal-engineer` — macOS Metal：Swift/Metal、3D 渲染
- `terminal-integration-specialist` — 终端集成：SwiftTerm、模拟器

## 28. 编排 / 治理 / 元智能体（combine 自身）

- `engineering-multi-agent-systems-architect` — 多智能体架构：拓扑、信任、故障恢复、HITL
- `agents-orchestrator` — 编排者：自主流水线编排、开发工作流领导
- `automation-governance-architect` — 自动化治理：n8n、价值/风险审计
- `specialized-workflow-architect` — 工作流设计：分支、故障模式、交接契约
- `identity-graph-operator` — 身份图谱（兼，见第 8）
- `agentic-identity-trust` — 身份信任（兼，见第 5）

---

## 附：非角色项（禁止选角，供内部运维参考）

以下 strategy 目录下的 16 项是**内部运营文档/流程模板**，不是可调度角色，不得喂给架构师：

`QUICKSTART`、`EXECUTIVE-BRIEF`、`nexus-strategy`、`handoff-templates`、`agent-activation-prompts`、`scenario-incident-response`、`scenario-marketing-campaign`、`scenario-enterprise-feature`、`scenario-startup-mvp`、`phase-0-discovery`、`phase-1-strategy`、`phase-2-foundation`、`phase-3-build`、`phase-4-hardening`、`phase-5-launch`、`phase-6-operate`