"""Shoulder MRI scoring configuration."""
from configs.base import AppConfig

SHOULDER_CONFIG = AppConfig(
    app_title="MSK Shoulder Data Collector",
    window_title="MSK Shoulder Data Collector",
    quality_items=[
        ("contrast_resolution",        "Contrast Resolution"),
        ("edge_sharpness",             "Edge Sharpness"),
        ("fat_suppression",            "Fat Suppression"),
        ("fluid_brightness",           "Fluid Brightness"),
        ("image_noise",                "Image Noise"),
        ("motion_artifact",            "Motion Artifact"),
        ("reconstruction_artifacts",   "Reconstruction Artifacts"),
        ("overall_image_quality",      "Overall Image Quality"),
    ],
    structure_items=[
        ("supraspinatus_infraspinatus_tendon_visibility", "Supraspinatus / Infraspinatus Tendon"),
        ("subscapularis_tendon_visibility",               "Subscapularis Tendon"),
        ("teres_minor_tendon_visibility",                 "Teres Minor Tendon"),
        ("glenoid_labrum_visibility",                     "Glenoid Labrum"),
        ("biceps_tendon_visibility",                      "Biceps Tendon"),
        ("articular_cartilage_visibility",                "Articular Cartilage"),
        ("bones_visibility",                              "Bones"),
        ("ac_joint_visibility",                           "AC Joint"),
    ],
    pathology_items=[
        ("supraspinatus_infraspinatus_tear", "Supraspinatus / Infraspinatus Tear", ["No Tear", "Partial Tear", "Full Thickness Tear"]),
        ("subscapularis_tear",               "Subscapularis Tear",                 ["No Tear", "Partial Tear", "Full Thickness Tear"]),
        ("superior_labral_tear",             "Superior Labral Tear",               ["No", "Yes"]),
        ("anteroinferior_labral_tear",       "Anteroinferior Labral Tear",         ["No", "Yes"]),
        ("biceps_tendon_tear",               "Biceps Tendon Tear",                 ["No", "Yes"]),
        ("articular_cartilage_defect",       "Articular Cartilage Defect",         ["None", "Partial Thickness", "Full Thickness"]),
        ("hill_sachs_deformity",             "Hill-Sachs Deformity",               ["No", "Yes"]),
        ("bankart_fracture",                 "Bankart Fracture",                   ["No", "Yes"]),
        ("subacromial_bursitis",             "Subacromial Bursitis",               ["No", "Yes"]),
        ("ac_oa",                            "AC Osteoarthritis",                  ["No", "Yes"]),
    ],
)
