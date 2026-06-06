import type { Metadata, Site, Socials } from "@types";

export const SITE: Site = {
  TITLE: "scout-agent",
  DESCRIPTION:
    "Building an AI ReAct agent that scouts basketball players from live sources — in public.",
  NUM_POSTS_ON_HOMEPAGE: 5,
};

export const HOME: Metadata = {
  TITLE: "scout-agent",
  DESCRIPTION:
    "An AI ReAct agent that researches basketball players and writes scouting reports for coaches and sporting directors. Built in public.",
};

export const BLOG: Metadata = {
  TITLE: "Devlog",
  DESCRIPTION: "Building scout-agent in public, one milestone at a time.",
};

export const SOCIALS: Socials = [
  {
    NAME: "GitHub",
    HREF: "https://github.com/ricardomm85/scout-agent",
  },
  {
    NAME: "LinkedIn",
    HREF: "https://www.linkedin.com/in/ricardo-full-stack/",
  },
];
