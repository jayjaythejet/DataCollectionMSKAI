"""Knee MRI scoring configuration."""
from configs.base import AppConfig

KNEE_CONFIG = AppConfig(
    app_title="MSK Knee Data Collector",
    window_title="MSK Knee Data Collector",
    quality_items=[
        ("contrast_resolution",    "Contrast Resolution"),
        ("edge_sharpness",         "Edge Sharpness"),
        ("fat_suppression",        "Fat Suppression"),
        ("fluid_brightness",       "Fluid Brightness"),
        ("image_noise",            "Image Noise"),
        ("motion_artifact",        "Motion Artifact"),
        ("partial_volume_effects", "Partial Volume Effects"),
        ("overall_image_quality",  "Overall Image Quality"),
    ],
    structure_items=[
        ("acl_visibility",                 "ACL"),
        ("pcl_visibility",                 "PCL"),
        ("mcl_visibility",                 "MCL"),
        ("lcl_visibility",                 "LCL"),
        ("medial_meniscus_visibility",     "Medial Meniscus"),
        ("lateral_meniscus_visibility",    "Lateral Meniscus"),
        ("extensor_tendons_visibility",    "Extensor Tendons"),
        ("articular_cartilage_visibility", "Articular Cartilage"),
        ("bones_visibility",               "Bones"),
    ],
    pathology_items=[
        ("acl_tear",                   "ACL Tear",                   ["Yes", "No"]),
        ("pcl_tear",                   "PCL Tear",                   ["Yes", "No"]),
        ("mcl_tear",                   "MCL Tear",                   ["Yes", "No"]),
        ("lcl_tear",                   "LCL Tear",                   ["Yes", "No"]),
        ("medial_meniscus_tear",       "Medial Meniscus Tear",       ["Yes", "No"]),
        ("lateral_meniscus_tear",      "Lateral Meniscus Tear",      ["Yes", "No"]),
        ("articular_cartilage_defect", "Articular Cartilage Defect", ["None", "Partial Thickness", "Full Thickness"]),
        ("bone_marrow_edema",          "Bone Marrow Edema",          ["Yes", "No"]),
    ],
)
