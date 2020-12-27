package net.gree_advertising.uranow.adapter

import android.support.v7.util.SortedList
import android.support.v7.widget.RecyclerView
import android.view.ViewGroup

abstract class SortedWithHeaderRecyclerViewAdapter <T, VH, HeaderVH>(
        private var headerViewHolder :HeaderVH
) : RecyclerView.Adapter<RecyclerView.ViewHolder>()
        where VH: RecyclerView.ViewHolder, HeaderVH :RecyclerView.ViewHolder {

    companion object {
        const val VIEW_TYPE_HEADER: Int = 0
        const val VIEW_TYPE_LIST: Int = 1
    }

    abstract var sortedList: SortedList<T>

    fun addItems(items :List<T>) {
        sortedList.addAll(items)
    }

    override fun getItemViewType(position: Int): Int {
        if (position == 0) {
            return VIEW_TYPE_HEADER
        }
        return VIEW_TYPE_LIST
    }

    override fun getItemCount(): Int {
        return sortedList.size() + 1
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when(viewType) {
            VIEW_TYPE_HEADER -> headerViewHolder
            else -> onCreateListItemViewHolder(parent)
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        if (position == 0) {
            @Suppress("UNCHECKED_CAST")
            return onBindHeaderViewHolder(holder as HeaderVH, position)
        }
        @Suppress("UNCHECKED_CAST")
        return onBindListItemViewHolder(holder as VH, position - 1)
    }

    abstract fun onCreateListItemViewHolder(parent: ViewGroup): VH

    abstract fun onBindHeaderViewHolder(holder :HeaderVH, position :Int)
    abstract fun onBindListItemViewHolder(holder :VH, position: Int)
}
