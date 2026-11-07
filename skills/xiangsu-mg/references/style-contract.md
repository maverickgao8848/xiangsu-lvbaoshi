# Style contract

Project-root `frame.md` is the effective visual source for scene builders. Resolve user changes there; keep scene content in BRIEF/STORYBOARD. Editorial children inherit the complete upstream frame and resources through [upstream-frame.md](upstream-frame.md).

## Style selection

| 中文名称 | Style ID | Status / resources |
|---|---|---|
| 青柠玻璃（Lime） | `glass-lime` | Default: [FRAME](../assets/styles/glass-lime/FRAME.md), [recipes](../assets/styles/glass-lime/recipes.md), fonts, dark dotted space, optical glass and lime accents |
| 白金黑纹理 | `baijin-black-texture` | Default: [FRAME](../assets/styles/baijin-black-texture/FRAME.md), fonts, original satin/grain background, warm-white titles and pale gold |
| 朱砂活字剧场 | `vermilion-theatre` | Active: [FRAME](../assets/styles/vermilion-theatre/FRAME.md), local fonts and approved A letterpress variant |
| 工程图册 | `gable-reed` | Active: [FRAME](../assets/styles/gable-reed/FRAME.md), dark engineering atlas and measured paths |
| 建筑剖面轴测 · 三维意境 | `architectural-section` | Active: [FRAME](../assets/styles/architectural-section/FRAME.md), local fonts and user-selected static 3D section reference |
| 钴蓝网格 | `cobalt-grid` | Archived pack: existing-project use and provenance |
| 终端手册 | `opencode` | Archived pack: existing-project use and provenance |
| 复古电脑目录 | `dell-1996` | Archived pack: existing-project use and provenance |
| 巨字海报 | `broadside` | Archived pack: existing-project use and provenance |

Offer Lime/Baijin when style is unresolved. An explicit request for Xiangsu MG’s colorful glass and dotted reference selects `glass-lime`, including for an editorial child; a generic mention of emerald alone is not enough to override a specific existing frame. An explicit choice supersedes a conflicting inherited frame; preserve project history when correcting an existing child under upstream-frame.md. Accept an explicit active-style or custom-frame choice. Present Chinese display names and resolve them to internal IDs. Archived-pack reactivation is a new visual-direction choice. Each pack's `metadata.json` records its exact resources, source and reviewed sample scope.

## Apply and inherit

From the Skill directory:

```sh
node scripts/apply-style.mjs --style glass-lime --project <project>
node scripts/apply-style.mjs --style baijin-black-texture --project <project>
node scripts/apply-style.mjs --style gable-reed --project <project>
node scripts/apply-style.mjs --style architectural-section --project <project>
node scripts/apply-style.mjs --style vermilion-theatre --project <project> [--variant <letterpress|rubber|signpaint>]
```

The loader verifies manifest hashes, writes effective `frame.md`, and stages resources under `assets/references/styles/<style-id>/`. Typography variants resolve into that single effective frame and `selection.json`. Identical application is unchanged; differing existing files require explicit reconciliation. Existing frozen projects retain their frame and assets until a requested revision.

`metadata.frameResources` declares portable dependencies. The loader writes their staged paths and hashes to `frame-resources.json`; keep it beside the frame for child inheritance. Include CSS/JS, fonts, textures and notices needed by the chosen runtime. `provenance/` holds historical source evidence.

## Material interfaces

- Lime: load its staged CSS/JS and initialize glass after layout as shown in FRAME. Adopt suitable scene recipes for the current teaching relationship.
- Baijin: load its scoped theme/background CSS/JS and initialize `BaijinTexture.blackBackground(stage, currentSceneTimeline, duration)` once at construction. Its background stays outside the camera world; sheen follows the same timeline.
- Vermilion: use `metadata.selection.approvedDefault` unless the user requests a variant comparison or change.
- Concrete objects follow [object-library.md](object-library.md). Semantic structure and motion follow visual-grammar and motion-direction.

Declare bundled fonts with `@font-face`; inspect actual family, weight and glyph resolution in the rendered browser. For an observed variable-font renderer failure, derive static instances of the intended weights from the same source. Required font files and notices travel with the project.

## Reference scope

Adopt composition, hierarchy, typography, density and material features from reference images, recording paths and scopes in STORYBOARD. Project facts and motion come from the current script and storyboard. Store source identity, revision, license and hashes in provenance; unknown values remain unknown. Sample-specific approval is recorded in metadata and assessed alongside the current preview under [quality.md](quality.md).
