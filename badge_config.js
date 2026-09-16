/**
 * badge_config.js - 全站平台与难度渲染的唯一配置文件
 * 新增平台或难度时，直接在此处扩展键值对即可。
 */
const BADGE_CONFIG = {
    platforms: {
        "Codeforces": { bg: "#e67e22", text: "#ffffff" },
        "QOJ":        { bg: "#363738", text: "#ffffff" },
        "Luogu":      { bg: "#35bddc", text: "#ffffff" },
        "AtCoder":    { bg: "#222222", text: "#ffffff" },
        "Nowcoder":   { bg: "#9b59b6", text: "#ffffff" },
        "default":    { bg: "#7f8c8d", text: "#ffffff" }
    },
    difficulties: {
        "Easy":       { bg: "#27ae60", text: "#ffffff", weight: 2 },
        "Medium":     { bg: "#f39c12", text: "#ffffff", weight: 3 },
        "Hard":       { bg: "#c0392b", text: "#ffffff", weight: 4 },
        "Template":    { bg: "#222222", text: "#ffffff", weight: 1 },
        "default":    { bg: "#95a5a6", text: "#ffffff", weight: 99 }
    }
};

/**
 * 获取平台的徽章 HTML
 */
function getPlatformBadge(platform) {
    const key = (platform || "").trim();
    const conf = BADGE_CONFIG.platforms[key] || BADGE_CONFIG.platforms["default"];
    return `<span class="badge" style="background-color: ${conf.bg}; color: ${conf.text};">${key || 'Unknown'}</span>`;
}

/**
 * 兼容比赛汇总页面的旧函数别名
 */
const getBadgeHtml = getPlatformBadge;

/**
 * 获取难度的徽章 HTML
 */
function getDiffBadge(diff) {
    const key = (diff || "").trim();
    const conf = BADGE_CONFIG.difficulties[key] || BADGE_CONFIG.difficulties["default"];
    return `<span class="badge" style="background-color: ${conf.bg}; color: ${conf.text};">${key || 'Unknown'}</span>`;
}

/**
 * 获取难度的排序权重（用于 Easy -> Medium -> Hard 升序排列）
 */
function getDiffWeight(diff) {
    const key = (diff || "").trim();
    const conf = BADGE_CONFIG.difficulties[key] || BADGE_CONFIG.difficulties["default"];
    return conf.weight;
}