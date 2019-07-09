[//]: # (Describe the project's purpose.)

## `mesa-aco` - Fedora Spec for mesa with Valve's Radeon ACO compiler patches from https://github.com/daniel-schuermann/mesa

The `mesa-aco` project goal is to provide an automated way for generating RPMs for Fedora through copr.

[//]: # (Describe the technology used.)

## What is mesa
[Mesa][1] project began as an open-source implementation of the OpenGL specification - a system for rendering interactive 3D graphics.
Over the years the project has grown to implement more graphics APIs, including OpenGL ES (versions 1, 2, 3), OpenCL, OpenMAX, VDPAU, VA API, XvMC and Vulkan.

## What is ACO
[ACO][2] is a New Compiler Backend created by ValveSoftware for RADV. Its main two goals are best-possible code generation for game shaders, and fastest-possible compilation speed
Official announcement can be found [here][2].

---
## **Contact info**

Maintainer:       'Mihai Vultur'<br />
Team:             'SRE Team'<br />

[1]: https://www.mesa3d.org/ "Mesa"
[2]: https://steamcommunity.com/games/221410/announcements/detail/1602634609636894200 "ACO"
