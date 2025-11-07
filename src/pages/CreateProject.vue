<template>
  <div class="project-container">
    <div class="project-card">
      <h2>Create New Project</h2>

      <form @submit.prevent="submitProject">
        <input
          v-model="project.title"
          type="text"
          class="form-input"
          placeholder="Project Title (English)"
          :readonly="isDean"
          required
        />

        <input
          v-model="project.title_kz"
          type="text"
          class="form-input"
          placeholder="Project Title (Kazakh)"
          :readonly="isDean"
          required
        />

        <input
          v-model="project.title_ru"
          type="text"
          class="form-input"
          placeholder="Project Title (Russian)"
          :readonly="isDean"
          required
        />

        <textarea
          v-model="project.description"
          class="form-textarea"
          placeholder="Project Description"
          :readonly="isDean"
          required
        ></textarea>
        
        <button
          v-if="!isDean"
          type="button"
          class="ai-enhance-btn"
          @click="enhanceDescription"
          :disabled="isEnhancing || quotaLoading || !project.description.trim() || project.description.trim().length < 10 || (quotaData && quotaData.topic_enhancements && quotaData.topic_enhancements.remaining <= 0)"
          :title="isEnhancing ? 'Enhancing all 3 titles + description...' : 'Enhance all 3 titles and description with AI'"
        >
          <span class="btn-content">
            <span class="stars">✨</span>
            {{ isEnhancing ? 'Enhancing All...' : 'Enhance with AI' }}
            <span v-if="quotaData && quotaData.topic_enhancements" class="counter">
              ({{ quotaData.topic_enhancements.remaining }}/{{ quotaData.topic_enhancements.limit }})
            </span>
          </span>
        </button>
        
        <div v-if="!isDean && quotaData && quotaData.topic_enhancements && quotaData.topic_enhancements.remaining <= 0" class="limit-warning">
          ⚠️ Daily AI enhancement limit reached ({{ quotaData.topic_enhancements.used }}/{{ quotaData.topic_enhancements.limit }}). Resets at midnight.
        </div>
        
        <div v-if="!isDean && !quotaLoading && quotaData && quotaData.topic_enhancements && quotaData.topic_enhancements.remaining > 0" class="quota-info">
          💡 {{ quotaData.topic_enhancements.remaining }} AI enhancement{{ quotaData.topic_enhancements.remaining !== 1 ? 's' : '' }} remaining today
        </div>

        <div v-if="!isDean">
          <h3 class="skill-title">Choose skills you need:</h3>
          <div class="skills-grid">
            <div
              v-for="skill in allSkills"
              :key="skill.id"
              :readonly="isDean"
              :class="[
                'skill-card',
                { selected: selectedSkills.includes(skill.id) },
              ]"
              @click="toggleSkill(skill.id)"
            >
              {{ skill.name }}
            </div>
          </div>
        </div>
        <button type="submit" class="create-btn" v-if="!isDean">
          {{ isEditMode ? "Update" : "Create" }}
        </button>
      </form>
      <div v-if="isEditMode && teamMembers.length" class="team-members-section">
        <h3>Team Members</h3>
        <ul class="member-list">
          <li
            v-for="member in teamMembers"
            :key="member.user"
            class="member-item"
          >
            <router-link
              :to="`/students/${member.user}`"
              class="member-info"
              title="View profile"
            >
              <img :src="getPhoto(member)" alt="Avatar" class="member-avatar" />
              <span class="member-name">
                {{ member.first_name }} {{ member.last_name }}
              </span>
            </router-link>

            <button
              v-if="(isDean || isOwner || isSupervisor) && member.user !== currentUser.id"
              class="remove-btn"
              @click="confirmRemoveMember(member)"
            >
              🗑
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
  <div v-if="showRemoveModal" class="modal-overlay">
    <div class="modal">
      <p>Are you sure you want to remove {{ memberToRemove.first_name }}?</p>
      <div class="modal-actions">
        <button class="cancel-btn" @click="showRemoveModal = false">No</button>
        <button class="confirm-btn" @click="removeMember">Yes</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import { useAuthStore } from "@/store/auth";
import { useRouter, useRoute } from "vue-router";
import apiConfig from "@/utils/apiConfig";
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const team = ref(null);
const teamMembers = ref([]);
const showRemoveModal = ref(false);
const memberToRemove = ref(null);
const isEditMode = ref(false);
const currentUser = authStore.user;
const isOwner = ref(false);
const isDean = computed(() => currentUser?.role === "Dean Office");
const projectOwnerId = ref(null);
const isSupervisor = ref(currentUser?.role === "Supervisor");
const allSkills = ref([]);
const selectedSkills = ref([]);
const projectId = ref(null);
const isEnhancing = ref(false);

// Backend quota state management
const quotaData = ref(null);
const quotaLoading = ref(false);
const rateLimitError = ref(null);

const getPhoto = (member) => {
  const photo = member.photo || member.user?.photo;
  if (!photo) {
    return new URL("../icons/default-avatar.png", import.meta.url).href;
  }
  return photo.startsWith("http") ? photo : `${apiConfig.baseURL}${photo}`;
};
const project = ref({
  title: "",
  title_kz: "",
  title_ru: "",
  description: "",
});

const loadTeam = async (topicId) => {
  try {
    let endpoint = `${apiConfig.baseURL}/api/teams/my/`;
    let response = null;
    let teamData = null;

    if (isDean.value) {
      // 👨‍🎓 Dean → получаем все команды и ищем по topicId
      response = await axios.get(`${apiConfig.baseURL}/api/teams/approved/`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });

      teamData = response.data.find(
        (team) => team.thesis_topic?.id === Number(topicId)
      );
    } else {
      // 👤 Supervisor, Student, Owner → как раньше
      response = await axios.get(endpoint, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });

      if (Array.isArray(response.data)) {
        teamData = response.data.find(
          (team) => team.thesis_topic?.id === Number(topicId)
        );
      } else {
        teamData = response.data;
      }
    }

    if (teamData) {
      team.value = teamData;

      const isCurrentUserStudent =
        currentUser?.role?.toLowerCase() === "student";
      const filteredMembers = isCurrentUserStudent
        ? teamData.members.filter((m) => m.user !== currentUser.id)
        : teamData.members;

      teamMembers.value = filteredMembers;
      isOwner.value = teamData.is_owner ?? false;

    } else {
      console.warn("⚠️ No matching team found for topic:", topicId);
    }
  } catch (err) {
    console.error("❌ Error loading team:", err);
  }
};


const confirmRemoveMember = (member) => {
  memberToRemove.value = member;
  showRemoveModal.value = true;
};

const removeMember = async () => {
  try {
    await axios.post(
      `${apiConfig.baseURL}/api/teams/${team.value.id}/remove-member/${memberToRemove.value.user}/`,
      {},
      { headers: { Authorization: `Bearer ${authStore.token}` } }
    );
    // Обновляем список участников
    teamMembers.value = teamMembers.value.filter(
      (m) => m.user !== memberToRemove.value.user
    );
    showRemoveModal.value = false;
    alert("Member removed successfully.");
  } catch (err) {
    console.error("Remove failed:", err);
    alert("Failed to remove member.");
  }
};

// Fetch user's AI quota from backend
const fetchQuota = async () => {
  quotaLoading.value = true;
  rateLimitError.value = null;
  
  try {
    const response = await axios.get(`${apiConfig.baseURL}/api/ai/quota/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    
    quotaData.value = response.data;
    console.log('✅ Quota loaded:', quotaData.value);
  } catch (err) {
    console.error('❌ Failed to fetch quota:', err);
    
    // Handle auth errors
    if (err.response?.status === 401) {
      console.error('Authentication failed - redirecting to login');
      router.push('/login');
    }
  } finally {
    quotaLoading.value = false;
  }
};

// Выбор скиллов
const toggleSkill = (id) => {
  if (selectedSkills.value.includes(id)) {
    selectedSkills.value = selectedSkills.value.filter((s) => s !== id);
  } else {
    if (selectedSkills.value.length >= 10) {
      alert("You can select up to 10 skills only.");
      return;
    }
    selectedSkills.value.push(id);
  }
};

// AI Enhancement
const enhanceDescription = async () => {
  const trimmedDescription = project.value.description.trim();
  
  // Validate description length
  if (!trimmedDescription) {
    alert("Please enter a description first.");
    return;
  }
  
  if (trimmedDescription.length < 10) {
    alert("Description must be at least 10 characters long for AI enhancement.");
    return;
  }
  
  if (trimmedDescription.length > 5000) {
    alert("Description is too long (max 5000 characters).");
    return;
  }

  // Validate title lengths (optional fields, but if provided must be <= 500 chars)
  const trimmedTitleEn = project.value.title?.trim() || '';
  const trimmedTitleKz = project.value.title_kz?.trim() || '';
  const trimmedTitleRu = project.value.title_ru?.trim() || '';

  if (trimmedTitleEn.length > 500) {
    alert("English title is too long (max 500 characters).");
    return;
  }
  if (trimmedTitleKz.length > 500) {
    alert("Kazakh title is too long (max 500 characters).");
    return;
  }
  if (trimmedTitleRu.length > 500) {
    alert("Russian title is too long (max 500 characters).");
    return;
  }

  isEnhancing.value = true;

  try {
    // Prepare payload with description and optional titles in all 3 languages
    const payload = {
      description: trimmedDescription,
      // Send titles only if they exist (all are optional)
      ...(trimmedTitleEn && { title_en: trimmedTitleEn }),
      ...(trimmedTitleKz && { title_kz: trimmedTitleKz }),
      ...(trimmedTitleRu && { title_ru: trimmedTitleRu }),
    };

    const response = await axios.post(
      `${apiConfig.baseURL}/api/topics/enhance-description/`,
      payload,
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );

    if (response.data) {
      // Update all 4 fields with AI-enhanced content
      if (response.data.enhanced_title_en) {
        project.value.title = response.data.enhanced_title_en;
      }
      if (response.data.enhanced_title_kz) {
        project.value.title_kz = response.data.enhanced_title_kz;
      }
      if (response.data.enhanced_title_ru) {
        project.value.title_ru = response.data.enhanced_title_ru;
      }
      if (response.data.enhanced_description) {
        project.value.description = response.data.enhanced_description;
      }

      // Refresh quota from backend after successful enhancement
      await fetchQuota();
      
      console.log('✅ AI enhanced all 3 titles and description!');
    } else {
      alert("AI enhancement completed but no response received.");
    }
  } catch (err) {
    console.error("Failed to enhance content", err.response?.data || err);
    
    // Handle 429 Rate Limit errors
    if (err.response?.status === 429) {
      const errorData = err.response?.data || {};
      
      // Check if it's a daily quota error (has resets_at field)
      if (errorData.resets_at) {
        rateLimitError.value = {
          type: 'quota',
          message: errorData.detail || `Daily limit reached (${errorData.used}/${errorData.limit}). Resets at midnight.`,
          resets_at: errorData.resets_at,
          used: errorData.used,
          limit: errorData.limit,
        };
        
        // Refresh quota to sync with backend
        await fetchQuota();
        
        alert(rateLimitError.value.message);
      } 
      // Otherwise it's a throttle error (has "seconds" in detail)
      else if (errorData.detail && errorData.detail.includes('seconds')) {
        const match = errorData.detail.match(/(\d+)\s+seconds?/);
        const waitSeconds = match ? parseInt(match[1]) : 60;
        
        rateLimitError.value = {
          type: 'throttle',
          message: errorData.detail,
          waitSeconds: waitSeconds,
        };
        
        alert(`Please wait ${waitSeconds} seconds before trying again.`);
      }
      else {
        // Generic 429 error
        rateLimitError.value = {
          type: 'unknown',
          message: errorData.detail || 'Rate limit exceeded. Please try again later.',
        };
        alert(rateLimitError.value.message);
      }
    }
    // Handle authentication errors
    else if (err.response?.status === 401) {
      alert("Authentication failed. Please log in again.");
      router.push("/login");
    } 
    // Handle validation errors
    else if (err.response?.status === 400 && err.response?.data?.error) {
      alert(err.response.data.error);
    }
    // Handle other errors
    else {
      alert("Failed to enhance content. Please try again.");
    }
  } finally {
    isEnhancing.value = false;
  }
};

// Отправка проекта
const submitProject = async () => {
  if (
    project.value.title.trim() === "" ||
    project.value.description.trim() === "" ||
    selectedSkills.value.length === 0
  ) {
    alert("All fields are required and at least 1 skill must be selected.");
    return;
  }

  const payload = {
    title: project.value.title,
    title_kz: project.value.title_kz,
    title_ru: project.value.title_ru,
    description: project.value.description,
    required_skills: selectedSkills.value,
  };

  try {
    if (isEditMode.value && projectId.value) {
      // Редактирование (PATCH)
      await axios.patch(
        `${apiConfig.baseURL}/api/topics/${projectId.value}/edit/`,
        payload,
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      alert("Project updated!");
    } else {
      // Создание (POST)
      await axios.post(`${apiConfig.baseURL}/api/topics/create/`, payload, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });
      alert("Project created!");
    }

    router.push("/profile");
  } catch (err) {
    console.error("Failed to submit project", err.response?.data || err);
    alert("Failed to submit project");
  }
};
onMounted(async () => {
  try {
    // Fetch AI quota first
    await fetchQuota();

    const skillsRes = await axios.get(
      `${apiConfig.baseURL}/api/profiles/skills/`,
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    allSkills.value = skillsRes.data;

    if (route.query.edit === "true" && route.query.projectId) {
      isEditMode.value = true;
      projectId.value = route.query.projectId;

      const projectRes = await axios.get(
        `${apiConfig.baseURL}/api/topics/${projectId.value}/`,
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );

      const data = projectRes.data;
      project.value.title = data.title;
      project.value.title_kz = data.title_kz;
      project.value.title_ru = data.title_ru;
      project.value.description = data.description;
      selectedSkills.value = data.required_skills.map((id) => Number(id));
      projectOwnerId.value = data.owner || null;
      isOwner.value = data.is_owner;

      await loadTeam(projectId.value);
    }
  } catch (err) {
    console.error("Failed to load data", err);
  }
});
</script>

<style scoped>
.project-container {
  display: flex;
  justify-content: center;
  padding: 60px 40px;
}

.project-card {
  background: #eef5fb;
  padding: 30px;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

h2 {
  font-weight: bold;
  margin-bottom: 20px;
  font-size: 22px;
  text-align: center;
}

.form-input,
.form-textarea {
  width: 100%;
  margin-bottom: 15px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 14px;
  resize: none;
}

.form-textarea {
  height: 200px;
  resize: vertical; /* Allow users to resize vertically if needed */
  min-height: 150px;
  max-height: 500px;
}

.ai-enhance-btn {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
  background-size: 200% 200%;
  color: white;
  border: none;
  padding: 14px 24px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  margin-bottom: 15px;
  position: relative;
  overflow: hidden;
  animation: gradientShift 3s ease infinite;
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.ai-enhance-btn .btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.ai-enhance-btn .stars {
  font-size: 18px;
}

.ai-enhance-btn .counter {
  font-size: 13px;
  opacity: 0.9;
  font-weight: 600;
}

.ai-enhance-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.ai-enhance-btn:active:not(:disabled) {
  transform: translateY(0);
}

.ai-enhance-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  animation: none;
  background: linear-gradient(135deg, #999 0%, #666 100%);
}

.limit-warning {
  background: #fff3cd;
  border: 1px solid #ffc107;
  color: #856404;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 15px;
  text-align: center;
  font-weight: 500;
}

.quota-info {
  background: #d1ecf1;
  border: 1px solid #bee5eb;
  color: #0c5460;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 15px;
  text-align: center;
  font-weight: 500;
}

.skill-title {
  font-weight: bold;
  margin: 10px 0;
  font-size: 16px;
}

.skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.skill-card {
  padding: 6px 14px;
  background: #f0f0f0;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: 0.3s ease;
}

.skill-card:hover {
  background-color: #d6eaff;
}

.skill-card.selected {
  background-color: #007bff;
  color: white;
  font-weight: bold;
}

.create-btn {
  width: 100%;
  background: #007bff;
  color: white;
  font-weight: bold;
  border: none;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.3s ease;
}

.create-btn:hover {
  background: #0056b3;
}
.team-members-section {
  margin-top: 30px;
}
.member-list {
  list-style: none;
  padding: 0;
}
.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 10px;
}
.member-info {
  display: flex;
  align-items: center;
  text-decoration: none;
  gap: 12px;
  color: #333;
}

.member-info:hover .member-name {
  text-decoration: underline;
}

.member-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #007bff;
}

.member-name {
  font-weight: 500;
  font-size: 18px;
}

.remove-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
}
.remove-btn:hover {
  background: #b02a37;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.modal {
  background: white;
  padding: 20px 30px;
  border-radius: 12px;
  text-align: center;
}
.modal-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}
.cancel-btn,
.confirm-btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}
.cancel-btn {
  background: #6c757d;
  color: white;
}
.confirm-btn {
  background: #dc3545;
  color: white;
}
</style>
