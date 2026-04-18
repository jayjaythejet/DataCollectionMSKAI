"""Knee MRI scoring configuration."""
from configs.base import AppConfig

KNEE_CONFIG = AppConfig(
    app_title="MSK Knee Data Collector",
    window_title="MSK Knee Data Collector",
    input_sheet_name="Drusinsky_knee",
    output_sheet_name="Drusinsky_knee",
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
        ("acl_tear",                   "ACL Tear",                   ["No", "Yes"]),
        ("pcl_tear",                   "PCL Tear",                   ["No", "Yes"]),
        ("mcl_tear",                   "MCL Tear",                   ["No", "Yes"]),
        ("lcl_tear",                   "LCL Tear",                   ["No", "Yes"]),
        ("medial_meniscus_tear",       "Medial Meniscus Tear",       ["No", "Yes"]),
        ("lateral_meniscus_tear",      "Lateral Meniscus Tear",      ["No", "Yes"]),
        ("articular_cartilage_defect", "Articular Cartilage Defect", ["None", "Partial Thickness", "Full Thickness"]),
        ("bone_marrow_edema",          "Bone Marrow Edema",          ["No", "Yes"]),
    ],
)
