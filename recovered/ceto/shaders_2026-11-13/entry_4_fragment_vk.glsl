#version 450
#define UNITY_SUPPORTS_UNIFORM_LOCATION 1
#if UNITY_SUPPORTS_UNIFORM_LOCATION
#define UNITY_LOCATION(x) layout(location = x)
#define UNITY_BINDING(x) layout(binding = x, std140)
#else
#define UNITY_LOCATION(x)
#define UNITY_BINDING(x) layout(std140)
#endif
layout(set=0, binding=1) uniform sampler2D Ceto_ButterFlyLookUp;
layout(set=0, binding=2) uniform sampler2D Ceto_ReadBuffer0;
layout(set=0, binding=3) uniform sampler2D Ceto_ReadBuffer1;
layout(set=0, binding=4) uniform sampler2D Ceto_ReadBuffer2;
layout(location=0) in vec2 vs_TEXCOORD0;
layout(location = 0) out vec4 SV_Target0;
layout(location = 1) out vec4 SV_Target1;
layout(location = 2) out vec4 SV_Target2;
vec4 u_xlat0;
vec4 u_xlat1;
vec4 u_xlat2;
vec4 u_xlat3;
vec4 u_xlat4;
vec4 u_xlat5;
vec2 u_xlat12;
void main()
{
    u_xlat0.y = vs_TEXCOORD0.y;
    u_xlat1.y = 0.0;
    u_xlat1.xw = vs_TEXCOORD0.xy;
    u_xlat2 = texture(Ceto_ButterFlyLookUp, u_xlat1.xy);
    u_xlat0.x = u_xlat2.y;
    u_xlat3 = texture(Ceto_ReadBuffer0, u_xlat0.xy);
    u_xlat12.xy = u_xlat2.ww * u_xlat3.yw;
    u_xlat4.xz = u_xlat2.zz * u_xlat3.xz + (-u_xlat12.xy);
    u_xlat4.y = dot(u_xlat2.wz, u_xlat3.xy);
    u_xlat4.w = dot(u_xlat2.wz, u_xlat3.zw);
    u_xlat1.z = u_xlat2.x;
    u_xlat3 = texture(Ceto_ReadBuffer0, u_xlat1.zw);
    SV_Target0 = u_xlat4 + u_xlat3;
    u_xlat3 = texture(Ceto_ReadBuffer1, u_xlat0.xy);
    u_xlat0 = texture(Ceto_ReadBuffer2, u_xlat0.xy);
    u_xlat1.xy = u_xlat2.ww * u_xlat3.yw;
    u_xlat4.xz = u_xlat2.zz * u_xlat3.xz + (-u_xlat1.xy);
    u_xlat5 = texture(Ceto_ReadBuffer1, u_xlat1.zw);
    u_xlat1 = texture(Ceto_ReadBuffer2, u_xlat1.zw);
    u_xlat4.y = dot(u_xlat2.wz, u_xlat3.xy);
    u_xlat4.w = dot(u_xlat2.wz, u_xlat3.zw);
    SV_Target1 = u_xlat4 + u_xlat5;
    u_xlat2.xy = u_xlat0.yw * u_xlat2.ww;
    u_xlat3.xz = u_xlat2.zz * u_xlat0.xz + (-u_xlat2.xy);
    u_xlat3.y = dot(u_xlat2.wz, u_xlat0.xy);
    u_xlat3.w = dot(u_xlat2.wz, u_xlat0.zw);
    SV_Target2 = u_xlat1 + u_xlat3;
    return;
}
