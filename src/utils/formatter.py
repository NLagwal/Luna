class ResponseFormatter:
    @staticmethod
    def format_faculty_profile(profile):
        p_data = f"FACULTY PROFILE: {profile.name}\n"
        p_data += f"Designation: {profile.designation}\n"
        if profile.contact_info: p_data += f"Contact: {profile.contact_info}\n"
        if profile.profile_pdf: p_data += f"Detailed Profile (PDF): {profile.profile_pdf}\n"
        if profile.biography: p_data += f"Biography: {profile.biography}\n"
        if profile.research_interests: p_data += f"Research Interests: {profile.research_interests}\n"
        if profile.open_projects: p_data += f"Projects: {profile.open_projects}\n"
        
        if profile.additional_info:
            for key, val in profile.additional_info.items():
                p_data += f"{key}: {val}\n"
        
        if profile.publication_profiles:
            p_data += "Publication Profiles: " + ", ".join([f"{k}: {v}" for k, v in profile.publication_profiles.items()]) + "\n"
        
        return p_data

    @staticmethod
    def format_source_footer(urls, trust_level="B"):
        if not urls:
            return ""
        
        valid_urls = [
            u for u in urls 
            if u and isinstance(u, str) and u.strip() and u.strip().lower() != "none"
        ]
        if not valid_urls:
            return ""
        
        seen = set()
        unique_urls = []
        for url in valid_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        footer = "\n\nSources:\n"
        for url in unique_urls:
            footer += f"- {url}\n"
        
        return footer

