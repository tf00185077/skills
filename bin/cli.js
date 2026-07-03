#!/usr/bin/env node
"use strict";

// think-like-fable installer.
// Copies the skill into the locations Claude Code and Codex CLI scan,
// so it can be invoked as /think-like-fable in both.

const fs = require("fs");
const path = require("path");
const os = require("os");

const SKILL_NAME = "think-like-fable";
const skillSrc = path.join(__dirname, "..", "skill", "SKILL.md");

const home = os.homedir();
const targets = [
	{
		harness: "Claude Code",
		file: path.join(home, ".claude", "skills", SKILL_NAME, "SKILL.md"),
		transform: (content) => content,
		how: "/" + SKILL_NAME + " (also auto-triggered by its description)",
	},
	{
		harness: "Codex CLI",
		file: path.join(home, ".codex", "prompts", SKILL_NAME + ".md"),
		// Codex custom prompts have no frontmatter concept; strip it.
		transform: stripFrontmatter,
		how: "/" + SKILL_NAME,
	},
];

function stripFrontmatter(content) {
	const m = content.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n/);
	return m ? content.slice(m[0].length) : content;
}

function install(quiet) {
	const content = fs.readFileSync(skillSrc, "utf8");
	for (const t of targets) {
		fs.mkdirSync(path.dirname(t.file), { recursive: true });
		fs.writeFileSync(t.file, t.transform(content));
		if (!quiet) {
			console.log("  installed  " + t.file);
			console.log("             " + t.harness + ": invoke with " + t.how);
		}
	}
	if (!quiet) {
		console.log("\nthink-like-fable installed. Restart open CLI sessions to pick it up.");
	}
}

function uninstall() {
	for (const t of targets) {
		const dir = t.file.endsWith("SKILL.md") ? path.dirname(t.file) : null;
		if (fs.existsSync(t.file)) {
			fs.rmSync(t.file);
			console.log("  removed    " + t.file);
		}
		if (dir && fs.existsSync(dir) && fs.readdirSync(dir).length === 0) {
			fs.rmdirSync(dir);
		}
	}
	console.log("\nthink-like-fable uninstalled.");
}

const args = process.argv.slice(2);
const cmd = args.find((a) => !a.startsWith("-")) || "install";
const fromPostinstall = args.includes("--from-postinstall");

if (fromPostinstall && process.env.THINK_LIKE_FABLE_SKIP_INSTALL) {
	process.exit(0);
}

try {
	if (cmd === "install") {
		install(false);
	} else if (cmd === "uninstall") {
		uninstall();
	} else {
		console.log("Usage: npx think-like-fable [install|uninstall]");
		process.exit(cmd === "help" ? 0 : 1);
	}
} catch (err) {
	// postinstall must never break the host npm install
	console.error("think-like-fable installer error: " + err.message);
	process.exit(fromPostinstall ? 0 : 1);
}
