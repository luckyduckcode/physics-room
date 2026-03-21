// Gaussian splat shader (Godot 4.x shader language)
// Designed for use with POINTS/point-sprite meshes or MultiMesh instances.
// This shader renders each point as a smooth Gaussian disk using POINT_COORD
// (the built-in per-fragment coordinate for point sprites).

shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_alpha_prepass, blend_mix;

uniform vec4 splat_color : hint_color = vec4(1.0, 0.6, 0.2, 1.0);
uniform float intensity = 1.0; // multiplies alpha
uniform float falloff = 8.0; // higher => tighter Gaussian

void fragment() {
    // POINT_COORD is available for point sprites and ranges (0..1) across the point
    vec2 pc = POINT_COORD;
    // center at (0.5,0.5)
    vec2 d = pc - vec2(0.5);
    float r2 = dot(d, d);
    // Gaussian weight exp(-falloff * r^2)
    float w = exp(-falloff * r2);

    ALBEDO = splat_color.rgb;
    ALPHA = clamp(splat_color.a * w * intensity, 0.0, 1.0);
}
